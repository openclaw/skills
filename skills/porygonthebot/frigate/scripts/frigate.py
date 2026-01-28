#!/usr/bin/env python3
"""
Frigate NVR Helper Script

Usage:
    python frigate.py list                    # List all cameras
    python frigate.py snapshot <camera>       # Get snapshot from camera
    python frigate.py events <camera>         # Get motion events for camera
    python frigate.py stream <camera>         # Get stream URL for camera

Environment variables:
    FRIGATE_URL   - Frigate server URL
    FRIGATE_USER  - Username
    FRIGATE_PASS  - Password
"""

import os
import sys
import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

FRIGATE_URL = os.environ.get("FRIGATE_URL", "https://server.local:8971/")
FRIGATE_USER = os.environ.get("FRIGATE_USER", "username")
FRIGATE_PASS = os.environ.get("FRIGATE_PASS", "")


def login():
    """Authenticate with Frigate and return a session."""
    session = requests.Session()
    response = session.post(
        f"{FRIGATE_URL}/api/login",
        json={"user": FRIGATE_USER, "password": FRIGATE_PASS},
        verify=False
    )
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        sys.exit(1)
    return session


def list_cameras(session):
    """List all cameras."""
    config = session.get(f"{FRIGATE_URL}/api/config", verify=False).json()
    cameras = list(config.get('cameras', {}).keys())
    for cam in cameras:
        cam_config = config['cameras'][cam]
        detect = cam_config.get('detect', {})
        print(f"  - {cam}: {detect.get('width', '?')}x{detect.get('height', '?')}")
    return cameras


def get_snapshot(session, camera_name, output_path=None):
    """Get snapshot from a camera."""
    response = session.get(
        f"{FRIGATE_URL}/api/{camera_name}/latest.jpg",
        verify=False
    )
    if response.status_code != 200:
        print(f"Failed to get snapshot: {response.status_code}")
        return None
    
    if output_path:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Saved to {output_path}")
    return response.content


def get_events(session, camera_name=None, limit=10):
    """Get motion events."""
    params = f"limit={limit}"
    if camera_name:
        params += f"&cameras={camera_name}"
    response = session.get(
        f"{FRIGATE_URL}/api/events?{params}",
        verify=False
    )
    events = response.json()
    for event in events[:limit]:
        print(f"  - {event.get('camera')}: {event.get('start_time')}")
    return events


def get_stream_url(session, camera_name):
    """Get stream URL for a camera."""
    config = session.get(f"{FRIGATE_URL}/api/config", verify=False).json()
    streams = config.get('go2rtc', {}).get('streams', {}).get(camera_name, [])
    if streams:
        print(f"  {camera_name}: {streams[0]}")
    return streams


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    session = login()
    
    if command == "list":
        print("Cameras:")
        list_cameras(session)
    elif command == "snapshot":
        camera = sys.argv[2] if len(sys.argv) > 2 else None
        if not camera:
            print("Usage: python frigate.py snapshot <camera_name>")
            sys.exit(1)
        output = sys.argv[3] if len(sys.argv) > 3 else None
        get_snapshot(session, camera, output)
    elif command == "events":
        camera = sys.argv[2] if len(sys.argv) > 2 else None
        print("Recent events:")
        get_events(session, camera)
    elif command == "stream":
        camera = sys.argv[2] if len(sys.argv) > 2 else None
        if not camera:
            cameras = list_cameras(session)
            print("\nAvailable cameras:")
            for cam in cameras:
                get_stream_url(session, cam)
        else:
            get_stream_url(session, camera)
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
