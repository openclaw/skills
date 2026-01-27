#!/usr/bin/env python3
"""
Poll Fliz video status until completion or failure.

Usage:
    python poll_status.py --api-key KEY --video-id UUID
    python poll_status.py --api-key KEY --video-id UUID --interval 20 --timeout 600
"""

import argparse
import os
import sys
import time
import requests

BASE_URL = "https://app.fliz.ai"
TIMEOUT = 30

# Terminal states
COMPLETE_STATES = {"complete"}
ERROR_STATES = {"failed", "failed_unrecoverable", "failed_go_back_to_user_action"}
BLOCKED_STATES = {"user_action", "block"}

# Processing steps in order
PROCESSING_STEPS = [
    "pending", "scrapping", "meta", "script", "image_prompt", "image_script",
    "image_generation", "image_analysis", "image_to_video", "speech",
    "transcribe", "fix_transcribe", "translation", "video",
    "video_rendering", "video_rendering_queue"
]


def get_video_status(api_key: str, video_id: str) -> dict:
    """Fetch video status from API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/rest/videos/{video_id}",
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            video = data.get("fliz_video_by_pk")
            if video:
                return {
                    "success": True,
                    "video": video
                }
            return {
                "success": False,
                "error": "Video not found"
            }
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_step_progress(step: str) -> str:
    """Get progress indicator for step."""
    if step in COMPLETE_STATES:
        return "✅"
    if step in ERROR_STATES:
        return "❌"
    if step in BLOCKED_STATES:
        return "⚠️"
    
    try:
        idx = PROCESSING_STEPS.index(step)
        total = len(PROCESSING_STEPS)
        pct = int((idx + 1) / total * 100)
        return f"⏳ {pct}%"
    except ValueError:
        return "🔄"


def poll_until_complete(api_key: str, video_id: str, 
                        interval: int = 15, timeout: int = 600) -> dict:
    """Poll video status until terminal state reached."""
    start_time = time.time()
    last_step = None
    
    print(f"Polling video: {video_id}")
    print(f"Interval: {interval}s, Timeout: {timeout}s")
    print("-" * 50)
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed > timeout:
            print(f"\n⏱️ Timeout reached after {int(elapsed)}s")
            return {
                "success": False,
                "error": "Timeout",
                "elapsed": elapsed
            }
        
        result = get_video_status(api_key, video_id)
        
        if not result["success"]:
            print(f"\n❌ Error: {result.get('error')}")
            return result
        
        video = result["video"]
        step = video.get("step", "unknown")
        
        # Print progress
        progress = get_step_progress(step)
        if step != last_step:
            print(f"{progress} Step: {step}")
            last_step = step
        
        # Check terminal states
        if step in COMPLETE_STATES:
            url = video.get("url")
            print(f"\n✅ Video complete!")
            print(f"   URL: {url}")
            return {
                "success": True,
                "video": video,
                "url": url,
                "elapsed": elapsed
            }
        
        if step in ERROR_STATES:
            error = video.get("error", {})
            print(f"\n❌ Video failed: {step}")
            print(f"   Error: {error}")
            return {
                "success": False,
                "video": video,
                "error": error,
                "elapsed": elapsed
            }
        
        if step in BLOCKED_STATES:
            print(f"\n⚠️ Video blocked: {step}")
            print("   Manual intervention required in Fliz dashboard")
            return {
                "success": False,
                "video": video,
                "blocked": True,
                "elapsed": elapsed
            }
        
        # Wait before next poll
        time.sleep(interval)


def main():
    parser = argparse.ArgumentParser(description="Poll Fliz video status")
    parser.add_argument("--api-key", "-k", help="Fliz API key (or FLIZ_API_KEY env)")
    parser.add_argument("--video-id", "-v", required=True, help="Video UUID")
    parser.add_argument("--interval", "-i", type=int, default=15,
                       help="Polling interval in seconds (default: 15)")
    parser.add_argument("--timeout", "-t", type=int, default=600,
                       help="Maximum wait time in seconds (default: 600)")
    parser.add_argument("--once", action="store_true",
                       help="Check status once without polling")
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("FLIZ_API_KEY")
    if not api_key:
        print("Error: API key required. Use --api-key or set FLIZ_API_KEY")
        sys.exit(1)
    
    if args.once:
        result = get_video_status(api_key, args.video_id)
        if result["success"]:
            video = result["video"]
            step = video.get("step")
            progress = get_step_progress(step)
            print(f"{progress} Status: {step}")
            if video.get("url"):
                print(f"   URL: {video['url']}")
        else:
            print(f"❌ Error: {result.get('error')}")
            sys.exit(1)
    else:
        result = poll_until_complete(
            api_key, args.video_id,
            interval=args.interval,
            timeout=args.timeout
        )
        
        if not result["success"]:
            sys.exit(1)


if __name__ == "__main__":
    main()
