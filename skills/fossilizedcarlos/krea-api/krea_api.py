#!/usr/bin/env python3
"""
Krea.ai API - Image Generation Skill

Usage:
    python krea_api.py --prompt "A beautiful sunset" --model flux

Or use as a module:
    from krea_api import KreaAPI
    api = KreaAPI(key_id="...", secret="...")
    urls = api.generate_and_wait(prompt="...")
"""

import json
import time
import urllib.request
import urllib.error
import argparse
from typing import Optional, List


class KreaAPI:
    """Client for Krea.ai image generation API."""
    
    BASE_URL = "https://api.krea.ai"
    
    # Available image models and their endpoints
    IMAGE_MODELS = {
        "flux": "/generate/image/bfl/flux-1-dev",
        "flux-kontext": "/generate/image/bfl/flux-1-dev-kontext",
        "flux-1.1-pro": "/generate/image/bfl/flux-1-1-pro",
        "flux-1.1-pro-ultra": "/generate/image/bfl/flux-1-1-pro-ultra",
        "nano-banana": "/generate/image/krea/nano-banana",
        "nano-banana-pro": "/generate/image/krea/nano-banana-pro",
        "imagen-3": "/generate/image/google/imagen-3",
        "imagen-4": "/generate/image/google/imagen-4",
        "imagen-4-fast": "/generate/image/google/imagen-4-fast",
        "imagen-4-ultra": "/generate/image/google/imagen-4-ultra",
        "ideogram-2.0a-turbo": "/generate/image/ideogram/ideogram-2-0a-turbo",
        "ideogram-3.0": "/generate/image/ideogram/ideogram-3-0",
        "seedream-3": "/generate/image/seedream/seedream-3",
        "seedream-4": "/generate/image/seedream/seedream-4",
        "chatgpt-image": "/generate/image/openai/chatgpt-image",
        "runway-gen-4": "/generate/image/runway/gen-4",
    }
    
    def __init__(self, key_id: str = None, secret: str = None):
        """
        Initialize the Krea API client.
        
        Args:
            key_id: Your API key ID (or set via config)
            secret: Your API secret (or set via config)
        """
        # Try config if not provided
        if not key_id or not secret:
            key_id = key_id or self._get_config("key_id")
            secret = secret or self._get_config("secret")
        
        if not key_id or not secret:
            raise ValueError("API credentials required. Set via args or clawdbot config.")
        
        self.token = f"{key_id}:{secret}"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (compatible; Klawf/1.0; +https://clawdhub.com/FossilizedCarlos/krea-api)"
        }
    
    def _get_config(self, key: str) -> Optional[str]:
        """Get config from clawdbot config if available."""
        try:
            import subprocess
            result = subprocess.run(
                ["clawdbot", "config", "get", f"skill.krea_api.{key}"],
                capture_output=True, text=True
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None
    
    def generate_image(
        self,
        prompt: str,
        model: str = "flux",
        width: int = 1024,
        height: int = 1024,
        steps: int = 25,
        guidance_scale: float = 3.0,
        seed: Optional[str] = None,
        webhook_url: Optional[str] = None,
    ) -> dict:
        """
        Create an image generation job.
        
        Args:
            prompt: Text description of the image (max 1800 chars)
            model: Model name (default: "flux")
            width: Image width (512-2368, default: 1024)
            height: Image height (512-2368, default: 1024)
            steps: Generation steps (1-100, default: 25)
            guidance_scale: Guidance scale (0-24, default: 3.0)
            seed: Random seed for reproducibility
            webhook_url: URL to receive completion notification
            
        Returns:
            dict with job_id, status, created_at
        """
        endpoint = self.IMAGE_MODELS.get(model)
        if not endpoint:
            raise ValueError(
                f"Unknown model: {model}. Available: {list(self.IMAGE_MODELS.keys())}"
            )
        
        url = f"{self.BASE_URL}{endpoint}"
        
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "guidance_scale_flux": guidance_scale,
        }
        
        if seed:
            payload["seed"] = seed
            
        headers = self.headers.copy()
        if webhook_url:
            headers["X-Webhook-URL"] = webhook_url
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), method="POST")
        for k, v in headers.items():
            req.add_header(k, v)
        
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    
    def get_job(self, job_id: str) -> dict:
        """Get the status and result of a job."""
        url = f"{self.BASE_URL}/jobs/{job_id}"
        req = urllib.request.Request(url, method="GET")
        for k, v in self.headers.items():
            # Content-Type is harmless on GET but unnecessary.
            if k.lower() == "content-type":
                continue
            req.add_header(k, v)

        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    
    def wait_for_completion(
        self,
        job_id: str,
        poll_interval: float = 2.0,
        timeout: float = 120.0
    ) -> dict:
        """Poll until job completes or times out."""
        start = time.time()
        while time.time() - start < timeout:
            job = self.get_job(job_id)
            status = job.get("status")
            
            if status == "completed":
                return job
            elif status == "failed":
                raise Exception(f"Job failed: {job}")
            elif status == "cancelled":
                raise Exception("Job was cancelled")
            
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")
    
    def generate_and_wait(self, prompt: str, **kwargs) -> List[str]:
        """Generate an image and wait for the result."""
        job = self.generate_image(prompt, **kwargs)
        print(f"Job created: {job['job_id']} (status: {job['status']})")
        
        result = self.wait_for_completion(job["job_id"])
        return result.get("result", {}).get("urls", [])


def main():
    parser = argparse.ArgumentParser(description="Generate images with Krea.ai API")
    parser.add_argument("--prompt", help="Image description")
    parser.add_argument("--model", default="flux", help="Model name (default: flux)")
    parser.add_argument("--width", type=int, default=1024, help="Image width")
    parser.add_argument("--height", type=int, default=1024, help="Image height")
    parser.add_argument("--key-id", help="API key ID")
    parser.add_argument("--secret", help="API secret")
    parser.add_argument("--list-models", action="store_true", help="List available models")

    args = parser.parse_args()

    if args.list_models:
        print("Available models:")
        for name in KreaAPI.IMAGE_MODELS:
            print(f"  - {name}")
        return

    if not args.prompt:
        parser.error("--prompt is required unless --list-models is set")

    api = KreaAPI(key_id=args.key_id, secret=args.secret)

    print(f"Generating '{args.prompt[:50]}...' with {args.model}...")
    urls = api.generate_and_wait(
        prompt=args.prompt,
        model=args.model,
        width=args.width,
        height=args.height
    )

    print("\nGenerated images:")
    for url in urls:
        print(f"  {url}")


if __name__ == "__main__":
    main()
