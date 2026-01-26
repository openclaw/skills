#!/usr/bin/env python3
"""
Homebridge API client for controlling smart home devices.

Usage:
    homebridge_api.py list [--room ROOM] [--type TYPE]
    homebridge_api.py get <accessory_id>
    homebridge_api.py set <accessory_id> <characteristic> <value>
    homebridge_api.py rooms

Reads credentials from ~/.clawdbot/clawdbot.json under skills.entries.homebridge:
    url: Homebridge Config UI X URL
    username: Admin username
    password: Admin password
"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def load_config() -> dict:
    """Load Homebridge config from credentials file."""
    config_path = Path.home() / ".clawdbot" / "credentials" / "homebridge.json"
    
    if not config_path.exists():
        print(f"Error: Config file not found at {config_path}", file=sys.stderr)
        print("Create it with: {\"url\": \"...\", \"username\": \"...\", \"password\": \"...\"}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
        sys.exit(1)
    
    for key in ["url", "username", "password"]:
        if not config.get(key):
            print(f"Error: Missing '{key}' in homebridge.json", file=sys.stderr)
            sys.exit(1)
    
    return config


def make_request(url: str, method: str = "GET", data: dict = None, token: str = None) -> dict:
    """Make HTTP request to Homebridge API."""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)
    
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        if error_body:
            print(f"Response: {error_body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def authenticate(base_url: str, username: str, password: str) -> str:
    """Authenticate and return access token."""
    url = f"{base_url}/api/auth/login"
    data = {"username": username, "password": password}
    response = make_request(url, method="POST", data=data)
    return response.get("access_token")


def list_accessories(base_url: str, token: str, room: str = None, acc_type: str = None) -> list:
    """List all accessories, optionally filtered by room or type."""
    url = f"{base_url}/api/accessories"
    accessories = make_request(url, token=token)
    
    results = []
    for acc in accessories:
        # Filter by type if specified
        if acc_type and acc.get("type") != acc_type:
            continue
        
        results.append({
            "uniqueId": acc.get("uniqueId"),
            "serviceName": acc.get("serviceName"),
            "type": acc.get("type"),
            "values": acc.get("values", {}),
        })
    
    # If room filter is specified, get layout and filter
    if room:
        layout_url = f"{base_url}/api/accessories/layout"
        layout = make_request(layout_url, token=token)
        
        room_ids = set()
        for r in layout:
            if room.lower() in r.get("name", "").lower():
                for service in r.get("services", []):
                    room_ids.add(service.get("uniqueId"))
        
        results = [acc for acc in results if acc["uniqueId"] in room_ids]
    
    return results


def get_accessory(base_url: str, token: str, accessory_id: str) -> dict:
    """Get details of a specific accessory."""
    url = f"{base_url}/api/accessories/{accessory_id}"
    return make_request(url, token=token)


def set_characteristic(base_url: str, token: str, accessory_id: str, 
                       characteristic: str, value) -> dict:
    """Set a characteristic value on an accessory."""
    url = f"{base_url}/api/accessories/{accessory_id}"
    
    # Convert value to appropriate type
    if isinstance(value, str):
        if value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        elif value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                pass
    
    data = {
        "characteristicType": characteristic,
        "value": value
    }
    return make_request(url, method="PUT", data=data, token=token)


def get_rooms(base_url: str, token: str) -> list:
    """Get room layout with accessories."""
    url = f"{base_url}/api/accessories/layout"
    layout = make_request(url, token=token)
    
    rooms = []
    for room in layout:
        rooms.append({
            "name": room.get("name"),
            "accessories": [s.get("serviceName") for s in room.get("services", [])]
        })
    return rooms


def main():
    parser = argparse.ArgumentParser(description="Homebridge API client")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List accessories")
    list_parser.add_argument("--room", help="Filter by room name")
    list_parser.add_argument("--type", dest="acc_type", help="Filter by accessory type")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get accessory details")
    get_parser.add_argument("accessory_id", help="Accessory unique ID")
    
    # Set command
    set_parser = subparsers.add_parser("set", help="Set accessory characteristic")
    set_parser.add_argument("accessory_id", help="Accessory unique ID")
    set_parser.add_argument("characteristic", help="Characteristic type (e.g., On, Brightness)")
    set_parser.add_argument("value", help="Value to set")
    
    # Rooms command
    subparsers.add_parser("rooms", help="List rooms and their accessories")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Load credentials from config
    config = load_config()
    base_url = config["url"].rstrip("/")
    username = config["username"]
    password = config["password"]
    
    # Authenticate
    token = authenticate(base_url, username, password)
    
    # Execute command
    if args.command == "list":
        result = list_accessories(base_url, token, args.room, args.acc_type)
    elif args.command == "get":
        result = get_accessory(base_url, token, args.accessory_id)
    elif args.command == "set":
        result = set_characteristic(base_url, token, args.accessory_id, 
                                    args.characteristic, args.value)
    elif args.command == "rooms":
        result = get_rooms(base_url, token)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
