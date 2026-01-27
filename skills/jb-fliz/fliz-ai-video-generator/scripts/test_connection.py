#!/usr/bin/env python3
"""
Test Fliz API connection and validate API key.

Usage:
    python test_connection.py --api-key YOUR_API_KEY
    python test_connection.py  # Uses FLIZ_API_KEY env var
"""

import argparse
import os
import sys
import requests

BASE_URL = "https://app.fliz.ai"
TIMEOUT = 30


def test_connection(api_key: str) -> dict:
    """Test API connection by fetching voices list."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/rest/voices",
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            voices = data.get("fliz_list_voices", {}).get("voices", [])
            return {
                "success": True,
                "message": "Connection successful!",
                "voices_count": len(voices),
                "status_code": 200
            }
        elif response.status_code == 401:
            return {
                "success": False,
                "message": "Invalid or expired API key",
                "status_code": 401
            }
        else:
            return {
                "success": False,
                "message": f"Unexpected response: {response.status_code}",
                "status_code": response.status_code,
                "body": response.text[:500]
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "message": "Request timed out"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Connection error: {str(e)}"
        }


def main():
    parser = argparse.ArgumentParser(description="Test Fliz API connection")
    parser.add_argument(
        "--api-key", "-k",
        help="Fliz API key (or set FLIZ_API_KEY env var)"
    )
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("FLIZ_API_KEY")
    
    if not api_key:
        print("Error: API key required. Use --api-key or set FLIZ_API_KEY env var")
        print("Get your API key at: https://app.fliz.ai/api-keys")
        sys.exit(1)
    
    print(f"Testing connection to {BASE_URL}...")
    print(f"API key: {api_key[:8]}...{api_key[-4:]}")
    print()
    
    result = test_connection(api_key)
    
    if result["success"]:
        print("✅ " + result["message"])
        print(f"   Found {result['voices_count']} available voices")
    else:
        print("❌ " + result["message"])
        if "body" in result:
            print(f"   Response: {result['body']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
