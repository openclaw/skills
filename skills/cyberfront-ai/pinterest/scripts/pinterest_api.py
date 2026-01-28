#!/usr/bin/env python3
"""
Pinterest API client for searching and browsing pins.
Supports both official API (with OAuth) and public search fallback.
"""

import argparse
import json
import os
import re
import sys
from urllib.parse import quote_plus, urljoin
from typing import Optional

try:
    import httpx
except ImportError:
    print("Installing httpx...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "-q"])
    import httpx


PINTEREST_API_BASE = "https://api.pinterest.com/v5"
PINTEREST_WEB_BASE = "https://www.pinterest.com"


def get_access_token() -> Optional[str]:
    """Get Pinterest access token from environment."""
    return os.environ.get("PINTEREST_ACCESS_TOKEN")


def api_request(endpoint: str, params: dict = None) -> dict:
    """Make authenticated request to Pinterest API."""
    token = get_access_token()
    if not token:
        raise ValueError("PINTEREST_ACCESS_TOKEN environment variable not set")
    
    url = f"{PINTEREST_API_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    with httpx.Client(timeout=30) as client:
        response = client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()


def search_pins_public(query: str, limit: int = 10) -> list:
    """
    Search Pinterest for pins using public web search.
    This works without API credentials.
    """
    # Pinterest's web search endpoint
    search_url = f"https://www.pinterest.com/resource/BaseSearchResource/get/"
    
    params = {
        "source_url": f"/search/pins/?q={quote_plus(query)}",
        "data": json.dumps({
            "options": {
                "query": query,
                "scope": "pins",
                "page_size": limit
            }
        })
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(search_url, params=params, headers=headers)
            
            if response.status_code != 200:
                # Fallback: scrape search results page
                return search_pins_scrape(query, limit)
            
            data = response.json()
            results = data.get("resource_response", {}).get("data", {}).get("results", [])
            
            pins = []
            for item in results[:limit]:
                if item.get("type") == "pin":
                    pin = {
                        "id": item.get("id"),
                        "title": item.get("title") or item.get("description", "")[:100],
                        "description": item.get("description"),
                        "image_url": get_best_image(item.get("images", {})),
                        "link": f"https://www.pinterest.com/pin/{item.get('id')}/",
                        "domain": item.get("domain"),
                        "save_count": item.get("repin_count", 0)
                    }
                    pins.append(pin)
            
            return pins
    except Exception as e:
        print(f"Web search failed: {e}, trying scrape method...")
        return search_pins_scrape(query, limit)


def search_pins_scrape(query: str, limit: int = 10) -> list:
    """
    Fallback: Scrape Pinterest search results page.
    """
    search_url = f"https://www.pinterest.com/search/pins/?q={quote_plus(query)}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    try:
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(search_url, headers=headers)
            html = response.text
            
            pins = []
            seen_ids = set()
            
            # Method 1: Look for pin data in script tags (Pinterest embeds JSON)
            # Pattern for pins with images
            pin_patterns = [
                # Full pin object pattern
                r'"id"\s*:\s*"(\d{15,20})"[^}]*?"images"\s*:\s*\{[^}]*?"originals"\s*:\s*\{\s*"url"\s*:\s*"([^"]+)"',
                # Simpler pattern for pin IDs with nearby image URLs
                r'"id"\s*:\s*"(\d{15,20})".*?"url"\s*:\s*"(https://i\.pinimg\.com/[^"]+)"',
                # Pattern for grid items
                r'data-pin-id="(\d+)".*?src="(https://i\.pinimg\.com/[^"]+)"',
            ]
            
            for pattern in pin_patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for pin_id, image_url in matches:
                    if pin_id not in seen_ids and len(pins) < limit:
                        seen_ids.add(pin_id)
                        # Clean up image URL - get highest quality
                        if '/236x/' in image_url:
                            image_url = image_url.replace('/236x/', '/736x/')
                        pins.append({
                            "id": pin_id,
                            "title": "",
                            "description": "",
                            "image_url": image_url,
                            "link": f"https://www.pinterest.com/pin/{pin_id}/",
                            "domain": "",
                            "save_count": 0
                        })
            
            # Method 2: If above didn't work, try finding all pinimg URLs with nearby IDs
            if not pins:
                # Find all image URLs
                img_matches = re.findall(r'(https://i\.pinimg\.com/\d+x/[a-f0-9/]+\.[a-z]+)', html)
                # Find all pin IDs
                id_matches = re.findall(r'"id"\s*:\s*"(\d{15,20})"', html)
                
                # Pair them up
                for i, (img_url, pin_id) in enumerate(zip(img_matches, id_matches)):
                    if i >= limit:
                        break
                    if pin_id not in seen_ids:
                        seen_ids.add(pin_id)
                        # Upgrade to larger image
                        img_url = re.sub(r'/\d+x/', '/736x/', img_url)
                        pins.append({
                            "id": pin_id,
                            "title": "",
                            "description": "",
                            "image_url": img_url,
                            "link": f"https://www.pinterest.com/pin/{pin_id}/",
                            "domain": "",
                            "save_count": 0
                        })
            
            return pins
    except Exception as e:
        print(f"Scrape failed: {e}")
        return []


def get_best_image(images: dict) -> str:
    """Get the best quality image URL from Pinterest image dict."""
    # Priority: orig > 736x > 564x > 474x > 236x
    for key in ["orig", "736x", "564x", "474x", "236x"]:
        if key in images:
            return images[key].get("url", "")
    return ""


def search_pins_api(query: str, limit: int = 10) -> list:
    """Search pins using official Pinterest API (requires OAuth)."""
    try:
        # Note: Standard API doesn't have public search
        # This searches user's own pins
        data = api_request("/pins", params={"page_size": min(limit, 100)})
        
        pins = []
        for item in data.get("items", []):
            pin = {
                "id": item.get("id"),
                "title": item.get("title"),
                "description": item.get("description"),
                "image_url": item.get("media", {}).get("images", {}).get("600x", {}).get("url"),
                "link": item.get("link"),
                "domain": item.get("domain"),
                "save_count": item.get("save_count", 0)
            }
            pins.append(pin)
        
        return pins
    except Exception as e:
        print(f"API search failed: {e}")
        return []


def get_pin(pin_id: str) -> dict:
    """Get details for a specific pin."""
    # Try API first
    token = get_access_token()
    if token:
        try:
            return api_request(f"/pins/{pin_id}")
        except:
            pass
    
    # Fallback: scrape pin page
    url = f"https://www.pinterest.com/pin/{pin_id}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        response = client.get(url, headers=headers)
        html = response.text
        
        # Extract data from page
        title_match = re.search(r'<title>([^<]+)</title>', html)
        image_match = re.search(r'"url":"(https://i\.pinimg\.com/originals/[^"]+)"', html)
        
        return {
            "id": pin_id,
            "title": title_match.group(1) if title_match else "",
            "image_url": image_match.group(1) if image_match else "",
            "link": url
        }


def get_boards() -> list:
    """Get user's boards (requires OAuth)."""
    data = api_request("/boards", params={"page_size": 100})
    return data.get("items", [])


def get_board_pins(board_id: str, limit: int = 25) -> list:
    """Get pins from a specific board."""
    data = api_request(f"/boards/{board_id}/pins", params={"page_size": min(limit, 100)})
    return data.get("items", [])


def format_pin(pin: dict) -> str:
    """Format a pin for display."""
    lines = []
    if pin.get("title"):
        lines.append(f"**{pin['title']}**")
    if pin.get("description"):
        desc = pin["description"][:200] + "..." if len(pin.get("description", "")) > 200 else pin.get("description", "")
        lines.append(desc)
    if pin.get("image_url"):
        lines.append(f"🖼 {pin['image_url']}")
    if pin.get("link"):
        lines.append(f"🔗 {pin['link']}")
    if pin.get("save_count"):
        lines.append(f"💾 {pin['save_count']} saves")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Pinterest API client")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for pins")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=5, help="Number of results")
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Pin details command
    pin_parser = subparsers.add_parser("pin", help="Get pin details")
    pin_parser.add_argument("pin_id", help="Pin ID")
    pin_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Boards command
    boards_parser = subparsers.add_parser("boards", help="List user's boards")
    boards_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Board pins command
    board_pins_parser = subparsers.add_parser("board-pins", help="Get pins from a board")
    board_pins_parser.add_argument("board_id", help="Board ID")
    board_pins_parser.add_argument("--limit", type=int, default=25, help="Number of results")
    board_pins_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.command == "search":
        pins = search_pins_public(args.query, args.limit)
        if args.json:
            print(json.dumps(pins, indent=2))
        else:
            print(f"Found {len(pins)} pins for '{args.query}':\n")
            for i, pin in enumerate(pins, 1):
                print(f"--- Pin {i} ---")
                print(format_pin(pin))
                print()
    
    elif args.command == "pin":
        pin = get_pin(args.pin_id)
        if args.json:
            print(json.dumps(pin, indent=2))
        else:
            print(format_pin(pin))
    
    elif args.command == "boards":
        boards = get_boards()
        if args.json:
            print(json.dumps(boards, indent=2))
        else:
            for board in boards:
                print(f"- {board.get('name')} (ID: {board.get('id')})")
    
    elif args.command == "board-pins":
        pins = get_board_pins(args.board_id, args.limit)
        if args.json:
            print(json.dumps(pins, indent=2))
        else:
            for i, pin in enumerate(pins, 1):
                print(f"--- Pin {i} ---")
                print(format_pin(pin))
                print()
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
