#!/usr/bin/env python3
"""
Kling Video Generation API Client.

Provides a wrapper for the Kling AI video generation API, supporting
image-to-video generation with first-last frame control.
"""

import base64
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import jwt
import requests


# =============================================================================
# Constants
# =============================================================================

API_BASE_URL = "https://api-beijing.klingai.com"
API_CREATE_TASK = "/v1/videos/image2video"
API_QUERY_TASK = "/v1/videos/image2video/{task_id}"

DEFAULT_MODEL = "kling-v2-6"
DEFAULT_DURATION = "5"
DEFAULT_MODE = "std"
DEFAULT_CFG_SCALE = 0.5
DEFAULT_TIMEOUT = 300
DEFAULT_POLL_INTERVAL = 5
DEFAULT_TOKEN_EXPIRE = 1800


# =============================================================================
# Exceptions
# =============================================================================

class KlingAPIError(Exception):
    """Base exception for Kling API errors."""
    pass


class KlingTaskError(KlingAPIError):
    """Exception for task-related errors."""
    pass


class KlingConfigError(KlingAPIError):
    """Exception for configuration errors."""
    pass


# =============================================================================
# Kling Video Generator
# =============================================================================

class KlingVideoGenerator:
    """Client for Kling video generation API."""

    def __init__(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ) -> None:
        """
        Initialize Kling API client.

        Args:
            access_key: API access key. If not provided, reads from KLING_ACCESS_KEY env var.
            secret_key: API secret key. If not provided, reads from KLING_SECRET_KEY env var.

        Raises:
            KlingConfigError: If API keys are not configured.
        """
        self.access_key = access_key or os.environ.get("KLING_ACCESS_KEY")
        self.secret_key = secret_key or os.environ.get("KLING_SECRET_KEY")

        if not self.access_key or not self.secret_key:
            raise KlingConfigError(
                "Kling API keys not configured.\n"
                "Please set in .env file:\n"
                "  KLING_ACCESS_KEY=your-access-key\n"
                "  KLING_SECRET_KEY=your-secret-key"
            )

        print("Kling API client initialized")
        print(f"  Access Key: {self.access_key[:8]}...{self.access_key[-4:]}")

    # -------------------------------------------------------------------------
    # Authentication
    # -------------------------------------------------------------------------

    def generate_jwt_token(self, expire_seconds: int = DEFAULT_TOKEN_EXPIRE) -> str:
        """
        Generate JWT token for API authentication.

        Args:
            expire_seconds: Token validity period in seconds.

        Returns:
            JWT token string.
        """
        current_time = int(time.time())

        headers = {"alg": "HS256", "typ": "JWT"}
        payload = {
            "iss": self.access_key,
            "exp": current_time + expire_seconds,
            "nbf": current_time - 5,
        }

        return jwt.encode(payload, self.secret_key, headers=headers)

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        return {
            "Authorization": f"Bearer {self.generate_jwt_token()}",
            "Content-Type": "application/json",
        }

    # -------------------------------------------------------------------------
    # Image Processing
    # -------------------------------------------------------------------------

    @staticmethod
    def _image_to_base64(image_path: str) -> str:
        """
        Convert image file to base64 string.

        Args:
            image_path: Path to image file.

        Returns:
            Base64-encoded string (without data: prefix).
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _prepare_image(self, image: str) -> str:
        """
        Prepare image for API request.

        Args:
            image: Image path or base64 string.

        Returns:
            Base64-encoded image string.
        """
        if os.path.exists(image):
            print(f"  Converting image: {Path(image).name}")
            return self._image_to_base64(image)
        return image

    # -------------------------------------------------------------------------
    # Task Management
    # -------------------------------------------------------------------------

    def create_video_task(
        self,
        image_start: str,
        image_end: Optional[str] = None,
        prompt: str = "",
        model_name: str = DEFAULT_MODEL,
        duration: str = DEFAULT_DURATION,
        mode: str = DEFAULT_MODE,
        cfg_scale: float = DEFAULT_CFG_SCALE,
        negative_prompt: str = "",
        callback_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create image-to-video generation task.

        Args:
            image_start: Start frame image path or base64 string.
            image_end: End frame image path or base64 string (optional).
            prompt: Positive prompt describing the transition.
            model_name: Model name (default: kling-v2-6).
            duration: Video duration in seconds (5 or 10).
            mode: Generation mode (std or pro).
            cfg_scale: Prompt adherence (0-1), only for V1.x models.
            negative_prompt: Negative prompt.
            callback_url: Callback URL for task completion.

        Returns:
            Task data dictionary with task_id and status.

        Raises:
            KlingAPIError: If task creation fails.
        """
        # Prepare images
        request_body = {
            "model_name": model_name,
            "image": self._prepare_image(image_start),
            "duration": duration,
            "mode": mode,
        }

        if image_end:
            request_body["image_tail"] = self._prepare_image(image_end)

        # Add optional parameters
        if prompt:
            request_body["prompt"] = prompt
        if negative_prompt:
            request_body["negative_prompt"] = negative_prompt
        if callback_url:
            request_body["callback_url"] = callback_url

        # cfg_scale only supported in V1.x models
        if not model_name.startswith("kling-v2"):
            request_body["cfg_scale"] = cfg_scale

        # Log task info
        video_type = "first-last frame" if image_end else "single frame animation"
        print(f"Creating video task...")
        print(f"  Model: {model_name}")
        print(f"  Mode: {mode}")
        print(f"  Duration: {duration}s")
        print(f"  Type: {video_type}")

        # Send request
        url = f"{API_BASE_URL}{API_CREATE_TASK}"
        response = requests.post(url, json=request_body, headers=self._get_auth_headers())

        self._check_response(response, "create task")

        result = response.json()
        task_data = result["data"]

        print(f"Task created successfully!")
        print(f"  Task ID: {task_data['task_id']}")
        print(f"  Status: {task_data['task_status']}")

        return task_data

    def query_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Query task status.

        Args:
            task_id: Task ID to query.

        Returns:
            Task data dictionary.

        Raises:
            KlingAPIError: If query fails.
        """
        url = f"{API_BASE_URL}{API_QUERY_TASK.format(task_id=task_id)}"
        response = requests.get(url, headers=self._get_auth_headers())

        self._check_response(response, "query task")
        return response.json()["data"]

    def wait_for_completion(
        self,
        task_id: str,
        timeout: int = DEFAULT_TIMEOUT,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
    ) -> Dict[str, Any]:
        """
        Wait for task completion by polling.

        Args:
            task_id: Task ID to wait for.
            timeout: Maximum wait time in seconds.
            poll_interval: Polling interval in seconds.

        Returns:
            Completed task data.

        Raises:
            TimeoutError: If task doesn't complete within timeout.
            KlingTaskError: If task fails.
        """
        print(f"Waiting for task completion (ID: {task_id})...")
        start_time = time.time()

        while True:
            elapsed = int(time.time() - start_time)

            if elapsed > timeout:
                raise TimeoutError(f"Task timeout after {elapsed}s (ID: {task_id})")

            task_data = self.query_task_status(task_id)
            status = task_data["task_status"]

            if status == "succeed":
                print(f"Task completed! Duration: {elapsed}s")
                return task_data

            if status == "failed":
                error_msg = task_data.get("task_status_msg", "Unknown error")
                raise KlingTaskError(f"Task failed (ID: {task_id}): {error_msg}")

            if status in ("submitted", "processing"):
                print(f"  [{elapsed}s] Status: {status}, waiting...")
                time.sleep(poll_interval)
            else:
                raise KlingTaskError(f"Unknown task status: {status}")

    # -------------------------------------------------------------------------
    # Video Download
    # -------------------------------------------------------------------------

    def download_video(self, video_url: str, save_path: str) -> str:
        """
        Download generated video.

        Args:
            video_url: URL of the video to download.
            save_path: Path to save the video.

        Returns:
            Path to saved video file.

        Raises:
            KlingAPIError: If download fails.
        """
        print(f"Downloading video...")
        print(f"  URL: {video_url}")
        print(f"  Save to: {save_path}")

        # Create directory if needed
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        # Download with streaming
        response = requests.get(video_url, stream=True)
        if response.status_code != 200:
            raise KlingAPIError(f"Download failed with status {response.status_code}")

        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        file_size_mb = os.path.getsize(save_path) / (1024 * 1024)
        print(f"Download complete! Size: {file_size_mb:.2f} MB")

        return save_path

    # -------------------------------------------------------------------------
    # High-Level API
    # -------------------------------------------------------------------------

    def generate_and_download(
        self,
        image_start: str,
        image_end: Optional[str],
        prompt: str,
        output_path: str,
        **kwargs: Any,
    ) -> str:
        """
        Generate video and download in one call.

        Args:
            image_start: Start frame image path.
            image_end: End frame image path (optional).
            prompt: Generation prompt.
            output_path: Path to save the video.
            **kwargs: Additional arguments for create_video_task().

        Returns:
            Path to downloaded video.

        Raises:
            KlingAPIError: If any step fails.
        """
        # Create task
        task_data = self.create_video_task(
            image_start=image_start,
            image_end=image_end,
            prompt=prompt,
            **kwargs,
        )

        # Wait for completion
        result_data = self.wait_for_completion(task_data["task_id"])

        # Get video URL
        videos = result_data.get("task_result", {}).get("videos", [])
        if not videos:
            raise KlingAPIError("Task completed but no video returned")

        # Download video
        return self.download_video(videos[0]["url"], output_path)

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------

    def _check_response(self, response: requests.Response, action: str) -> None:
        """
        Check API response for errors.

        Args:
            response: HTTP response object.
            action: Description of the action for error messages.

        Raises:
            KlingAPIError: If response indicates an error.
        """
        if response.status_code != 200:
            raise KlingAPIError(
                f"Failed to {action}:\n"
                f"  Status: {response.status_code}\n"
                f"  Response: {response.text}"
            )

        result = response.json()
        if result.get("code") != 0:
            raise KlingAPIError(
                f"Failed to {action}:\n"
                f"  Error code: {result.get('code')}\n"
                f"  Message: {result.get('message')}"
            )


# =============================================================================
# Main (for testing)
# =============================================================================

if __name__ == "__main__":
    # Test JWT token generation
    generator = KlingVideoGenerator()
    token = generator.generate_jwt_token()
    print(f"\nGenerated JWT Token: {token[:50]}...")
