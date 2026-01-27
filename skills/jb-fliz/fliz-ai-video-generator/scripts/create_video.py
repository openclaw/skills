#!/usr/bin/env python3
"""
Create a Fliz video from text content.

Usage:
    python create_video.py --api-key KEY --name "Title" --description "Content..."
    python create_video.py --api-key KEY --file content.txt --name "Title"
    python create_video.py --api-key KEY --name "Title" --description "Content" --format size_9_16 --lang fr
"""

import argparse
import json
import os
import sys
import requests

BASE_URL = "https://app.fliz.ai"
TIMEOUT = 60


def create_video(api_key: str, params: dict) -> dict:
    """Create a new video via Fliz API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Build request body
    body = {
        "fliz_video_create_input": params
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/rest/video",
            headers=headers,
            json=body,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            result = data.get("fliz_video_create", {})
            return {
                "success": True,
                "video_id": result.get("video_id")
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


def main():
    parser = argparse.ArgumentParser(description="Create Fliz video from text")
    parser.add_argument("--api-key", "-k", help="Fliz API key (or FLIZ_API_KEY env)")
    parser.add_argument("--name", "-n", required=True, help="Video title")
    parser.add_argument("--description", "-d", help="Video content text")
    parser.add_argument("--file", "-f", help="Read content from file")
    parser.add_argument("--format", default="size_16_9", 
                       choices=["size_16_9", "size_9_16", "square"],
                       help="Video format (default: size_16_9)")
    parser.add_argument("--lang", "-l", default="en", help="Language code (default: en)")
    parser.add_argument("--category", default="article",
                       choices=["article", "product", "ad"],
                       help="Video category (default: article)")
    parser.add_argument("--script-style", help="Script style enum")
    parser.add_argument("--image-style", help="Image style enum")
    parser.add_argument("--webhook-url", help="Webhook callback URL")
    parser.add_argument("--output", "-o", help="Save response to JSON file")
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("FLIZ_API_KEY")
    if not api_key:
        print("Error: API key required. Use --api-key or set FLIZ_API_KEY")
        sys.exit(1)
    
    # Get description from file or argument
    description = args.description
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                description = f.read()
        except IOError as e:
            print(f"Error reading file: {e}")
            sys.exit(1)
    
    if not description:
        print("Error: Description required. Use --description or --file")
        sys.exit(1)
    
    # Build parameters
    params = {
        "name": args.name,
        "description": description,
        "format": args.format,
        "lang": args.lang,
        "category": args.category,
        "is_automatic": True
    }
    
    # Add optional parameters
    if args.script_style:
        params["script_style"] = args.script_style
    if args.image_style:
        params["image_style"] = args.image_style
    if args.webhook_url:
        params["webhook_url"] = args.webhook_url
    
    print(f"Creating video: {args.name}")
    print(f"Format: {args.format}, Language: {args.lang}")
    print(f"Content length: {len(description)} characters")
    print()
    
    result = create_video(api_key, params)
    
    if result["success"]:
        print("✅ Video created successfully!")
        print(f"   Video ID: {result['video_id']}")
        print()
        print(f"Check status: GET /api/rest/videos/{result['video_id']}")
        
        if args.output:
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
            print(f"Response saved to: {args.output}")
    else:
        print("❌ Failed to create video")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        if "status_code" in result:
            print(f"   Status: {result['status_code']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
