"""Oura API client wrapper."""

import os
import sys
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


class OuraClient:
    """Client for interacting with the Oura API v2."""

    BASE_URL = "https://api.ouraring.com/v2"

    def __init__(self, access_token: str | None = None) -> None:
        """
        Initialize the Oura API client.

        Args:
            access_token: Oura API personal access token. If not provided,
                         loads from secrets/oura.env file.
        """
        if access_token is None:
            access_token = self._load_token()

        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})

    def _load_token(self) -> str:
        """Load access token from environment or secrets file.

        Tries in order:
        1. PERSONAL_ACCESS_TOKEN environment variable
        2. ./secrets/oura.env file
        3. ~/.secrets/oura.env file
        """
        # 1. Check if already set in environment
        token = os.getenv("PERSONAL_ACCESS_TOKEN")
        if token:
            return token

        # 2. Try ./secrets/oura.env (current directory)
        local_secrets_file = Path.cwd() / "secrets" / "oura.env"
        if local_secrets_file.exists():
            load_dotenv(local_secrets_file)
            token = os.getenv("PERSONAL_ACCESS_TOKEN")
            if token:
                return token

        # 3. Try ~/.secrets/oura.env (home directory)
        home_secrets_file = Path.home() / ".secrets" / "oura.env"
        if home_secrets_file.exists():
            load_dotenv(home_secrets_file)
            token = os.getenv("PERSONAL_ACCESS_TOKEN")
            if token:
                return token

        # None of the methods worked
        print(
            "Error: PERSONAL_ACCESS_TOKEN not found.\n\n"
            "Please set it via:\n"
            "  1. Environment variable: export PERSONAL_ACCESS_TOKEN=<your_token>\n"
            "  2. Local file: ./secrets/oura.env\n"
            "  3. Home file: ~/.secrets/oura.env\n\n"
            "Obtain a token at: https://cloud.ouraring.com/personal-access-tokens",
            file=sys.stderr,
        )
        sys.exit(1)

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Make GET request to Oura API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response as dictionary
        """
        url = f"{self.BASE_URL}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        result: dict[str, Any] = response.json()
        return result

    def _get_date_range_data(
        self, endpoint: str, start_date: str, end_date: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Generic method for date-range endpoints.

        Args:
            endpoint: API endpoint path (e.g., 'usercollection/daily_activity')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            next_token: Optional pagination token

        Returns:
            JSON response as dictionary
        """
        params = {"start_date": start_date, "end_date": end_date}
        if next_token:
            params["next_token"] = next_token
        return self._get(endpoint, params)

    def get_daily_activity(
        self, start_date: str, end_date: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Get daily activity data."""
        return self._get_date_range_data(
            "usercollection/daily_activity", start_date, end_date, next_token
        )

    def get_daily_sleep(
        self, start_date: str, end_date: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Get daily sleep data."""
        return self._get_date_range_data(
            "usercollection/daily_sleep", start_date, end_date, next_token
        )

    def get_daily_readiness(
        self, start_date: str, end_date: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Get daily readiness data."""
        return self._get_date_range_data(
            "usercollection/daily_readiness", start_date, end_date, next_token
        )

    def get_daily_spo2(
        self, start_date: str, end_date: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Get daily SpO2 data."""
        return self._get_date_range_data(
            "usercollection/daily_spo2", start_date, end_date, next_token
        )

    def get_daily_stress(
        self, start_date: str, end_date: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Get daily stress data."""
        return self._get_date_range_data(
            "usercollection/daily_stress", start_date, end_date, next_token
        )

    def get_heartrate(
        self, start_datetime: str, end_datetime: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Get heart rate time series data."""
        params = {"start_datetime": start_datetime, "end_datetime": end_datetime}
        if next_token:
            params["next_token"] = next_token
        return self._get("usercollection/heartrate", params)

    def get_workouts(
        self, start_date: str, end_date: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Get workout data."""
        return self._get_date_range_data("usercollection/workout", start_date, end_date, next_token)

    def get_sessions(
        self, start_date: str, end_date: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Get session data."""
        return self._get_date_range_data("usercollection/session", start_date, end_date, next_token)

    def get_tags(
        self, start_date: str, end_date: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Get tag data."""
        return self._get_date_range_data("usercollection/tag", start_date, end_date, next_token)

    def get_rest_mode_periods(
        self, start_date: str, end_date: str, next_token: str | None = None
    ) -> dict[str, Any]:
        """Get rest mode periods."""
        return self._get_date_range_data(
            "usercollection/rest_mode_period", start_date, end_date, next_token
        )

    def get_personal_info(self) -> dict[str, Any]:
        """Get personal information."""
        return self._get("usercollection/personal_info")

    def get_all_data(self, start_date: str, end_date: str) -> dict[str, list[dict[str, Any]]]:
        """
        Get all available data for the specified date range.

        Returns:
            Dictionary with keys for each data type containing their respective data
        """
        all_data: dict[str, list[dict[str, Any]]] = {}

        # Collect all data types
        try:
            all_data["activity"] = self.get_daily_activity(start_date, end_date).get("data", [])
        except Exception:
            all_data["activity"] = []

        try:
            all_data["sleep"] = self.get_daily_sleep(start_date, end_date).get("data", [])
        except Exception:
            all_data["sleep"] = []

        try:
            all_data["readiness"] = self.get_daily_readiness(start_date, end_date).get("data", [])
        except Exception:
            all_data["readiness"] = []

        try:
            all_data["spo2"] = self.get_daily_spo2(start_date, end_date).get("data", [])
        except Exception:
            all_data["spo2"] = []

        try:
            all_data["stress"] = self.get_daily_stress(start_date, end_date).get("data", [])
        except Exception:
            all_data["stress"] = []

        try:
            # Convert dates to datetime format for heartrate endpoint
            start_datetime = f"{start_date}T00:00:00"
            end_datetime = f"{end_date}T23:59:59"
            all_data["heartrate"] = self.get_heartrate(start_datetime, end_datetime).get("data", [])
        except Exception:
            all_data["heartrate"] = []

        try:
            all_data["workouts"] = self.get_workouts(start_date, end_date).get("data", [])
        except Exception:
            all_data["workouts"] = []

        try:
            all_data["sessions"] = self.get_sessions(start_date, end_date).get("data", [])
        except Exception:
            all_data["sessions"] = []

        try:
            all_data["tags"] = self.get_tags(start_date, end_date).get("data", [])
        except Exception:
            all_data["tags"] = []

        try:
            all_data["rest_mode"] = self.get_rest_mode_periods(start_date, end_date).get("data", [])
        except Exception:
            all_data["rest_mode"] = []

        try:
            all_data["personal_info"] = [self.get_personal_info()]
        except Exception:
            all_data["personal_info"] = []

        return all_data
