#!/usr/bin/env python3
"""
WHOOP API Client
Handles authentication and API requests to WHOOP REST API.
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Iterator

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install with: pip3 install requests")
    sys.exit(1)

WHOOP_BASE_URL = "https://api.prod.whoop.com/developer"
CREDENTIALS_PATH = Path.home() / ".whoop" / "credentials.json"
TOKEN_PATH = Path.home() / ".whoop" / "token.json"


class WhoopClient:
    def __init__(self):
        self.base_url = WHOOP_BASE_URL
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self._load_token()

    def _load_credentials(self) -> Dict[str, str]:
        """Load client_id and client_secret from credentials file."""
        if not CREDENTIALS_PATH.exists():
            raise FileNotFoundError(
                f"Credentials not found at {CREDENTIALS_PATH}\n"
                'Create the file with: {"client_id": "...", "client_secret": "..."}'
            )
        with open(CREDENTIALS_PATH) as f:
            creds = json.load(f)
        if "client_id" not in creds or "client_secret" not in creds:
            raise ValueError(
                "credentials.json missing required fields: client_id, client_secret"
            )
        return creds

    def _load_token(self):
        """Load access/refresh tokens from token file."""
        if TOKEN_PATH.exists():
            try:
                with open(TOKEN_PATH) as f:
                    data = json.load(f)
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                expires_at = data.get("expires_at")
                if expires_at:
                    self.token_expires_at = datetime.fromisoformat(expires_at)
            except (json.JSONDecodeError, KeyError, ValueError):
                # Corrupted token file — ignore and require re-auth
                pass

    def _save_token(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: int = 3600,
    ):
        """Save tokens to file."""
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc)
        data = {
            "access_token": access_token,
            "refresh_token": refresh_token or self.refresh_token,
            "updated_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=expires_in)).isoformat(),
        }
        with open(TOKEN_PATH, "w") as f:
            json.dump(data, f, indent=2)
        os.chmod(TOKEN_PATH, 0o600)
        self.access_token = access_token
        self.token_expires_at = now + timedelta(seconds=expires_in)
        if refresh_token:
            self.refresh_token = refresh_token

    def _is_token_expired(self) -> bool:
        """Check if the access token is expired or about to expire."""
        if not self.token_expires_at:
            return False
        # Treat as expired 60 seconds before actual expiry
        return datetime.now(timezone.utc) >= (
            self.token_expires_at - timedelta(seconds=60)
        )

    def authenticate(self, authorization_code: str, redirect_uri: str):
        """
        Exchange authorization code for access token.

        Args:
            authorization_code: Code from OAuth redirect
            redirect_uri: Must match the redirect_uri used in the authorization URL
        """
        creds = self._load_credentials()
        response = requests.post(
            "https://api.prod.whoop.com/oauth/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "code": authorization_code,
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
                "redirect_uri": redirect_uri,
            },
        )
        response.raise_for_status()
        data = response.json()
        self._save_token(
            data["access_token"],
            data.get("refresh_token"),
            data.get("expires_in", 3600),
        )

    def _refresh_access_token(self):
        """Refresh the access token using refresh token."""
        if not self.refresh_token:
            raise ValueError(
                "No refresh token available. Re-run the authorization flow."
            )

        creds = self._load_credentials()
        response = requests.post(
            "https://api.prod.whoop.com/oauth/oauth2/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": creds["client_id"],
                "client_secret": creds["client_secret"],
            },
        )
        response.raise_for_status()
        data = response.json()
        self._save_token(
            data["access_token"],
            data.get("refresh_token"),
            data.get("expires_in", 3600),
        )

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request with auto-refresh and rate limit handling."""
        if not self.access_token:
            raise ValueError(
                "Not authenticated. Run authenticate() first or obtain a token.\n"
                "See references/oauth.md for setup instructions."
            )

        # Proactively refresh if token is expired
        if self._is_token_expired() and self.refresh_token:
            self._refresh_access_token()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"

        response = requests.request(
            method, f"{self.base_url}{endpoint}", headers=headers, **kwargs
        )

        # Try refreshing token on 401
        if response.status_code == 401 and self.refresh_token:
            self._refresh_access_token()
            headers["Authorization"] = f"Bearer {self.access_token}"
            response = requests.request(
                method, f"{self.base_url}{endpoint}", headers=headers, **kwargs
            )

        # Handle rate limiting with retry
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited. Retrying in {retry_after} seconds...", file=sys.stderr)
            time.sleep(retry_after)
            response = requests.request(
                method, f"{self.base_url}{endpoint}", headers=headers, **kwargs
            )

        response.raise_for_status()
        return response.json()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET request."""
        return self._request("GET", endpoint, params=params)

    # --- User endpoints ---

    def get_profile(self) -> Dict[str, Any]:
        """Get user profile (name, email)."""
        return self.get("/v1/user/profile/basic")

    def get_body_measurements(self) -> Dict[str, Any]:
        """Get body measurements (height, weight, max HR)."""
        return self.get("/v1/user/measurement/body")

    # --- Recovery endpoints ---

    def get_recovery_collection(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 25,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get recovery records (paginated)."""
        params: Dict[str, Any] = {"limit": limit}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if next_token:
            params["nextToken"] = next_token
        return self.get("/v2/recovery", params=params)

    def get_recovery_for_cycle(self, cycle_id: int) -> Dict[str, Any]:
        """Get recovery for specific cycle."""
        return self.get(f"/v2/cycle/{cycle_id}/recovery")

    def iter_recovery(
        self, start: Optional[str] = None, end: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        """Iterate all recovery records with automatic pagination."""
        next_token = None
        while True:
            resp = self.get_recovery_collection(start, end, limit=25, next_token=next_token)
            for record in resp.get("records", []):
                yield record
            next_token = resp.get("next_token")
            if not next_token:
                break

    # --- Sleep endpoints ---

    def get_sleep_collection(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 25,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get sleep records (paginated)."""
        params: Dict[str, Any] = {"limit": limit}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if next_token:
            params["nextToken"] = next_token
        return self.get("/v2/activity/sleep", params=params)

    def get_sleep_by_id(self, sleep_id: str) -> Dict[str, Any]:
        """Get specific sleep by ID."""
        return self.get(f"/v2/activity/sleep/{sleep_id}")

    def get_sleep_for_cycle(self, cycle_id: int) -> Dict[str, Any]:
        """Get sleep for specific cycle."""
        return self.get(f"/v2/cycle/{cycle_id}/sleep")

    def iter_sleep(
        self, start: Optional[str] = None, end: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        """Iterate all sleep records with automatic pagination."""
        next_token = None
        while True:
            resp = self.get_sleep_collection(start, end, limit=25, next_token=next_token)
            for record in resp.get("records", []):
                yield record
            next_token = resp.get("next_token")
            if not next_token:
                break

    # --- Cycle endpoints ---

    def get_cycle_collection(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 25,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get physiological cycles (paginated)."""
        params: Dict[str, Any] = {"limit": limit}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if next_token:
            params["nextToken"] = next_token
        return self.get("/v1/cycle", params=params)

    def get_cycle_by_id(self, cycle_id: int) -> Dict[str, Any]:
        """Get specific cycle by ID."""
        return self.get(f"/v1/cycle/{cycle_id}")

    def iter_cycles(
        self, start: Optional[str] = None, end: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        """Iterate all cycles with automatic pagination."""
        next_token = None
        while True:
            resp = self.get_cycle_collection(start, end, limit=25, next_token=next_token)
            for record in resp.get("records", []):
                yield record
            next_token = resp.get("next_token")
            if not next_token:
                break

    # --- Workout endpoints ---

    def get_workout_collection(
        self,
        start: Optional[str] = None,
        end: Optional[str] = None,
        limit: int = 25,
        next_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get workouts (paginated)."""
        params: Dict[str, Any] = {"limit": limit}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        if next_token:
            params["nextToken"] = next_token
        return self.get("/v2/activity/workout", params=params)

    def get_workout_by_id(self, workout_id: str) -> Dict[str, Any]:
        """Get specific workout by ID."""
        return self.get(f"/v2/activity/workout/{workout_id}")

    def iter_workouts(
        self, start: Optional[str] = None, end: Optional[str] = None
    ) -> Iterator[Dict[str, Any]]:
        """Iterate all workouts with automatic pagination."""
        next_token = None
        while True:
            resp = self.get_workout_collection(start, end, limit=25, next_token=next_token)
            for record in resp.get("records", []):
                yield record
            next_token = resp.get("next_token")
            if not next_token:
                break
