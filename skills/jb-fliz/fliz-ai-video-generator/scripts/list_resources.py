#!/usr/bin/env python3
"""
List available Fliz resources (voices and music tracks).

Usage:
    python list_resources.py --api-key KEY --voices
    python list_resources.py --api-key KEY --musics
    python list_resources.py --api-key KEY --all
    python list_resources.py --api-key KEY --voices --json
"""

import argparse
import json
import os
import sys
import requests

BASE_URL = "https://app.fliz.ai"
TIMEOUT = 30


def get_voices(api_key: str) -> dict:
    """Fetch available voices."""
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
            return {"success": True, "voices": voices}
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def get_musics(api_key: str) -> dict:
    """Fetch available music tracks."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/rest/musics",
            headers=headers,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            musics = data.get("fliz_list_musics", {}).get("musics", [])
            return {"success": True, "musics": musics}
        else:
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text
            }
            
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}


def print_voices(voices: list, as_json: bool = False):
    """Display voices list."""
    if as_json:
        print(json.dumps(voices, indent=2))
        return
    
    print(f"\n🎙️ Available Voices ({len(voices)} total)")
    print("=" * 60)
    
    # Group by gender
    by_gender = {}
    for voice in voices:
        gender = voice.get("gender", "unknown")
        if gender not in by_gender:
            by_gender[gender] = []
        by_gender[gender].append(voice)
    
    for gender, items in sorted(by_gender.items()):
        print(f"\n{gender.upper()} ({len(items)})")
        print("-" * 40)
        for voice in items:
            vid = voice.get("id", "N/A")
            name = voice.get("name", "Unknown")
            print(f"  {vid:<30} {name}")


def print_musics(musics: list, as_json: bool = False):
    """Display music tracks list."""
    if as_json:
        print(json.dumps(musics, indent=2))
        return
    
    print(f"\n🎵 Available Music Tracks ({len(musics)} total)")
    print("=" * 60)
    
    # Group by theme
    by_theme = {}
    for music in musics:
        theme = music.get("theme", "unknown")
        if theme not in by_theme:
            by_theme[theme] = []
        by_theme[theme].append(music)
    
    for theme, items in sorted(by_theme.items()):
        print(f"\n{theme.upper()} ({len(items)})")
        print("-" * 40)
        for music in items:
            mid = music.get("id", "N/A")
            name = music.get("name", "Unknown")
            print(f"  {mid:<30} {name}")


def main():
    parser = argparse.ArgumentParser(description="List Fliz resources")
    parser.add_argument("--api-key", "-k", help="Fliz API key (or FLIZ_API_KEY env)")
    parser.add_argument("--voices", "-v", action="store_true", help="List voices")
    parser.add_argument("--musics", "-m", action="store_true", help="List music tracks")
    parser.add_argument("--all", "-a", action="store_true", help="List all resources")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    parser.add_argument("--output", "-o", help="Save to file")
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("FLIZ_API_KEY")
    if not api_key:
        print("Error: API key required. Use --api-key or set FLIZ_API_KEY")
        sys.exit(1)
    
    if not (args.voices or args.musics or args.all):
        print("Error: Specify --voices, --musics, or --all")
        sys.exit(1)
    
    output_data = {}
    
    if args.voices or args.all:
        result = get_voices(api_key)
        if result["success"]:
            output_data["voices"] = result["voices"]
            if not args.json:
                print_voices(result["voices"], args.json)
        else:
            print(f"❌ Failed to fetch voices: {result.get('error')}")
            sys.exit(1)
    
    if args.musics or args.all:
        result = get_musics(api_key)
        if result["success"]:
            output_data["musics"] = result["musics"]
            if not args.json:
                print_musics(result["musics"], args.json)
        else:
            print(f"❌ Failed to fetch musics: {result.get('error')}")
            sys.exit(1)
    
    if args.json:
        print(json.dumps(output_data, indent=2))
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nSaved to: {args.output}")


if __name__ == "__main__":
    main()
