"""
Fliz API Python Client

A complete Python wrapper for the Fliz REST API.
Supports video creation, status monitoring, translation, and resource listing.

Installation:
    pip install requests

Usage:
    from python_client import FlizClient
    
    client = FlizClient("YOUR_API_KEY")
    
    # Create video
    result = client.create_video(
        name="My Video",
        description="Full article content here...",
        format="size_16_9",
        lang="en"
    )
    
    # Wait for completion
    video = client.wait_for_video(result["video_id"])
    print(f"Video URL: {video['url']}")
"""

import time
from typing import Optional, Dict, List, Any
import requests


class FlizAPIError(Exception):
    """Custom exception for Fliz API errors."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class FlizClient:
    """
    Fliz API Client
    
    Attributes:
        api_key: Your Fliz API key from https://app.fliz.ai/api-keys
        base_url: API base URL (default: https://app.fliz.ai)
        timeout: Request timeout in seconds (default: 60)
    """
    
    BASE_URL = "https://app.fliz.ai"
    
    # Terminal states for video processing
    COMPLETE_STATES = {"complete"}
    ERROR_STATES = {"failed", "failed_unrecoverable", "failed_go_back_to_user_action"}
    BLOCKED_STATES = {"user_action", "block"}
    
    def __init__(self, api_key: str, base_url: str = None, timeout: int = 60):
        """
        Initialize Fliz client.
        
        Args:
            api_key: Your Fliz API key
            base_url: Optional custom base URL
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, 
                 params: dict = None, json_data: dict = None) -> dict:
        """Make API request with error handling."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self._session.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                timeout=self.timeout
            )
            
            if response.status_code == 401:
                raise FlizAPIError(
                    "Invalid or expired API key",
                    status_code=401
                )
            
            if response.status_code == 429:
                raise FlizAPIError(
                    "Rate limit exceeded. Please retry later.",
                    status_code=429
                )
            
            if response.status_code >= 400:
                raise FlizAPIError(
                    f"API error: {response.text}",
                    status_code=response.status_code,
                    response=response.json() if response.text else None
                )
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise FlizAPIError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise FlizAPIError(f"Connection error: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test API connection by fetching voices.
        
        Returns:
            True if connection successful
            
        Raises:
            FlizAPIError: If connection fails
        """
        self.get_voices()
        return True
    
    # ========== Video Operations ==========
    
    def create_video(
        self,
        name: str,
        description: str,
        format: str = "size_16_9",
        lang: str = "en",
        category: str = "article",
        script_style: str = None,
        image_style: str = None,
        image_urls: List[str] = None,
        caption_style: str = None,
        caption_position: str = None,
        caption_font: str = None,
        caption_color: str = None,
        caption_uppercase: bool = None,
        voice_id: str = None,
        is_male_voice: bool = None,
        music_id: str = None,
        music_url: str = None,
        music_volume: int = None,
        watermark_url: str = None,
        site_url: str = None,
        site_name: str = None,
        webhook_url: str = None,
        is_automatic: bool = True,
        video_animation_mode: str = None
    ) -> Dict[str, Any]:
        """
        Create a new video.
        
        Args:
            name: Video title (required)
            description: Full text content to transform (required)
            format: Video format - size_16_9, size_9_16, or square
            lang: Language ISO code (en, fr, es, etc.)
            category: article, product, or ad
            script_style: Narrative style enum
            image_style: Visual style enum
            image_urls: List of image URLs (required for product/ad)
            caption_style: Subtitle style
            caption_position: bottom or center
            caption_font: Font family
            caption_color: Hex color (#FFFFFF)
            caption_uppercase: Uppercase captions
            voice_id: Custom voice ID
            is_male_voice: Use male voice
            music_id: Background music ID
            music_url: Custom music URL
            music_volume: Volume 0-100
            watermark_url: Watermark image URL
            site_url: Call-to-action URL
            site_name: Call-to-action text
            webhook_url: Callback URL for completion
            is_automatic: Auto-process to completion
            video_animation_mode: full_video or hook_only
            
        Returns:
            dict with video_id
            
        Example:
            result = client.create_video(
                name="My Article",
                description="Full article text...",
                format="size_9_16",
                lang="fr",
                image_style="digital_art"
            )
        """
        # Build params dict, excluding None values
        params = {
            "name": name,
            "description": description,
            "format": format,
            "lang": lang,
            "category": category,
            "is_automatic": is_automatic
        }
        
        # Add optional params
        optional = {
            "script_style": script_style,
            "image_style": image_style,
            "image_urls": image_urls,
            "caption_style": caption_style,
            "caption_position": caption_position,
            "caption_font": caption_font,
            "caption_color": caption_color,
            "caption_uppercase": caption_uppercase,
            "voice_id": voice_id,
            "is_male_voice": is_male_voice,
            "music_id": music_id,
            "music_url": music_url,
            "music_volume": music_volume,
            "watermark_url": watermark_url,
            "site_url": site_url,
            "site_name": site_name,
            "webhook_url": webhook_url,
            "video_animation_mode": video_animation_mode
        }
        
        for key, value in optional.items():
            if value is not None:
                params[key] = value
        
        body = {"fliz_video_create_input": params}
        response = self._request("POST", "/api/rest/video", json_data=body)
        
        return response.get("fliz_video_create", {})
    
    def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Get video details by ID.
        
        Args:
            video_id: Video UUID
            
        Returns:
            Video object or None if not found
        """
        response = self._request("GET", f"/api/rest/videos/{video_id}")
        return response.get("fliz_video_by_pk")
    
    def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """
        Get simplified video status.
        
        Args:
            video_id: Video UUID
            
        Returns:
            dict with step, url, error, is_complete, is_error, is_blocked
        """
        video = self.get_video(video_id)
        
        if not video:
            raise FlizAPIError(f"Video not found: {video_id}")
        
        step = video.get("step", "unknown")
        
        return {
            "step": step,
            "url": video.get("url"),
            "error": video.get("error"),
            "is_complete": step in self.COMPLETE_STATES,
            "is_error": step in self.ERROR_STATES,
            "is_blocked": step in self.BLOCKED_STATES,
            "video": video
        }
    
    def list_videos(self, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List videos with pagination.
        
        Args:
            limit: Number of results
            offset: Pagination offset
            
        Returns:
            List of video objects
        """
        response = self._request(
            "GET", "/api/rest/videos",
            params={"limit": limit, "offset": offset}
        )
        return response.get("fliz_video", [])
    
    def wait_for_video(
        self,
        video_id: str,
        poll_interval: int = 15,
        timeout: int = 600,
        callback: callable = None
    ) -> Dict[str, Any]:
        """
        Poll video status until completion or failure.
        
        Args:
            video_id: Video UUID
            poll_interval: Seconds between polls
            timeout: Maximum wait time
            callback: Optional function called on each poll with status dict
            
        Returns:
            Final video object
            
        Raises:
            FlizAPIError: If video fails or times out
        """
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            
            if elapsed > timeout:
                raise FlizAPIError(
                    f"Timeout after {int(elapsed)}s waiting for video",
                    response={"video_id": video_id}
                )
            
            status = self.get_video_status(video_id)
            
            if callback:
                callback(status)
            
            if status["is_complete"]:
                return status["video"]
            
            if status["is_error"]:
                raise FlizAPIError(
                    f"Video failed: {status['step']}",
                    response=status["video"]
                )
            
            if status["is_blocked"]:
                raise FlizAPIError(
                    f"Video blocked: {status['step']} - manual intervention required",
                    response=status["video"]
                )
            
            time.sleep(poll_interval)
    
    def translate_video(
        self,
        video_id: str,
        new_lang: str,
        is_automatic: bool = True,
        webhook_url: str = None
    ) -> Dict[str, Any]:
        """
        Translate existing video to new language.
        
        Args:
            video_id: Source video UUID
            new_lang: Target language ISO code
            is_automatic: Auto-process
            webhook_url: Callback URL
            
        Returns:
            dict with new_video_id and cost
        """
        params = {"new_lang": new_lang}
        if is_automatic is not None:
            params["is_automatic"] = is_automatic
        if webhook_url:
            params["webhook_url"] = webhook_url
        
        response = self._request(
            "POST",
            f"/api/rest/videos/{video_id}/translate",
            params=params
        )
        return response.get("fliz_video_translate", {})
    
    def duplicate_video(self, video_id: str) -> Dict[str, Any]:
        """
        Duplicate existing video.
        
        Args:
            video_id: Source video UUID
            
        Returns:
            dict with new_video_id
        """
        response = self._request(
            "POST",
            f"/api/rest/videos/{video_id}/duplicate"
        )
        return response.get("fliz_video_duplicate", {})
    
    # ========== Resources ==========
    
    def get_voices(self) -> List[Dict[str, Any]]:
        """
        Get available text-to-speech voices.
        
        Returns:
            List of voice objects with id, name, gender, samples
        """
        response = self._request("GET", "/api/rest/voices")
        return response.get("fliz_list_voices", {}).get("voices", [])
    
    def get_musics(self) -> List[Dict[str, Any]]:
        """
        Get available background music tracks.
        
        Returns:
            List of music objects with id, name, theme, url
        """
        response = self._request("GET", "/api/rest/musics")
        return response.get("fliz_list_musics", {}).get("musics", [])


# ========== Example Usage ==========

if __name__ == "__main__":
    import os
    
    API_KEY = os.environ.get("FLIZ_API_KEY", "your-api-key-here")
    
    # Initialize client
    client = FlizClient(API_KEY)
    
    # Test connection
    try:
        client.test_connection()
        print("✅ Connection successful!")
    except FlizAPIError as e:
        print(f"❌ Connection failed: {e}")
        exit(1)
    
    # List available voices
    voices = client.get_voices()
    print(f"\n🎙️ Found {len(voices)} voices")
    
    # Create a video
    print("\n📹 Creating video...")
    result = client.create_video(
        name="Test Video",
        description="This is a test video created via the Fliz API.",
        format="size_16_9",
        lang="en",
        image_style="digital_art"
    )
    print(f"   Video ID: {result['video_id']}")
    
    # Wait for completion with progress callback
    def on_progress(status):
        print(f"   Status: {status['step']}")
    
    print("\n⏳ Waiting for video...")
    try:
        video = client.wait_for_video(
            result["video_id"],
            poll_interval=10,
            callback=on_progress
        )
        print(f"\n✅ Video ready: {video['url']}")
    except FlizAPIError as e:
        print(f"\n❌ Error: {e}")
