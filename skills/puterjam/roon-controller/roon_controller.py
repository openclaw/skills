#!/usr/bin/env python3
"""
Roon Player Controller
Supports: play/pause, previous track, next track, get current track
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict, List, Any

try:
    from roonapi import RoonApi, RoonDiscovery
except ImportError:
    print("error: Not installed roonapi")
    print("plz install roonapi: pip install roonapi")
    raise


class RoonController:
    """Roon Controller"""

    # Configuration storage path
    CONFIG_DIR = Path.home() / "clawd"
    CONFIG_FILE = CONFIG_DIR / "roon_config.json"

    # Application information
    APP_INFO = {
        "extension_id": "clawdbot-music-control",
        "display_name": "Clawdbot Music Control",
        "display_version": "1.0.0",
        "publisher": "Clawdbot",
        "email": "clawdbot@muspi.ai"
    }

    def __init__(self, host: str = None, port: int = None, verbose: bool = False):
        """
        Initialize Roon controller

        Args:
            host: Roon Core host address (None means auto-discovery)
            port: Roon API port (default 9100)
            verbose: whether to output detailed logs
        """
        self.host = host
        self.port = port if port else 9100
        self.verbose = verbose
        self.roon = None
        self.token = None
        self.core_id = None
        self.selected_zone = None  # User-selected zone name

        # Ensure directory exists
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Load saved configuration
        self._load_config()

        # Connect to Roon
        self._connect()

    def _load_config(self) -> None:
        """Load saved configuration (core_id, token, selected_zone, host, port)"""
        import json
        self.saved_host = None
        self.saved_port = None
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                self.core_id = config.get('core_id') or None
                self.token = config.get('token') or None
                self.selected_zone = config.get('selected_zone') or None
                self.saved_host = config.get('host') or None
                self.saved_port = config.get('port') or None
                if self.verbose:
                    print(f"✓ Loaded Roon configuration")
                    if self.saved_host:
                        print(f"  Saved address: {self.saved_host}:{self.saved_port}")
                    if self.selected_zone:
                        print(f"  Current zone: {self.selected_zone}")
            except Exception:
                if self.verbose:
                    print("⚠  Configuration file corrupted, will re-authorize")
        else:
            if self.verbose:
                print("ℹ  No saved configuration found, will perform new authorization")

    def _save_config(self) -> None:
        """Save configuration to file"""
        import json
        config = {
            'core_id': self.core_id,
            'token': self.token,
            'selected_zone': self.selected_zone,
            'host': self.host,
            'port': self.port
        }
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        if self.verbose:
            print(f"✓ Roon configuration saved (address: {self.host}:{self.port})")

    def _discover_roon_core(self, max_retries: int = 3) -> Optional[str]:
        """Auto-discover Roon Core with retry support"""
        for attempt in range(max_retries):
            try:
                if self.verbose:
                    if attempt > 0:
                        print(f"Retrying Roon Core discovery ({attempt + 1}/{max_retries})...")
                    else:
                        print(f"Discovering Roon Core... (core_id: {self.core_id or 'none'})")

                # Create discovery instance, pass core_id to speed up discovery
                discovery = RoonDiscovery(self.core_id)
                server = discovery.first()
                discovery.stop()

                if server:
                    host, port = server
                    self.host = host
                    self.port = int(port)
                    if self.verbose:
                        print(f"✓ Found Roon Core: {host}:{port}")
                    return host

                # Discovery failed, wait and retry
                if attempt < max_retries - 1:
                    time.sleep(1)

            except Exception as e:
                if self.verbose:
                    print(f"⚠  Auto-discovery failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1)

        return None

    def _try_connect(self, host: str, port: int) -> bool:
        """Try to connect to specified Roon Core address"""
        try:
            if self.verbose:
                print(f"Connecting to Roon Core ({host}:{port})...")

            self.roon = RoonApi(
                appinfo=self.APP_INFO,
                token=self.token,
                host=host,
                port=port,
                blocking_init=True
            )

            # Verify connection succeeded
            if self.roon and self.roon.token:
                self.host = host
                self.port = port
                return True
            return False
        except Exception as e:
            if self.verbose:
                print(f"⚠  Connection failed: {e}")
            return False

    def _connect(self) -> None:
        """Connect to Roon Core"""
        try:
            # 1. If host is specified on command line, use it directly
            if self.host is not None:
                if self._try_connect(self.host, self.port):
                    self._finalize_connection()
                    return
                raise Exception(f"Cannot connect to specified address {self.host}:{self.port}")

            # 2. Try using saved address
            if self.saved_host:
                if self.verbose:
                    print(f"Trying saved address: {self.saved_host}:{self.saved_port}")
                if self._try_connect(self.saved_host, self.saved_port or 9100):
                    self._finalize_connection()
                    return
                if self.verbose:
                    print("Saved address unavailable, trying auto-discovery...")

            # 3. Auto-discovery
            discovered_host = self._discover_roon_core()
            if discovered_host:
                if self._try_connect(self.host, self.port):
                    self._finalize_connection()
                    return

            raise Exception("Cannot connect to Roon Core")

        except Exception as e:
            raise Exception(f"Failed to connect to Roon: {e}")

    def _finalize_connection(self) -> None:
        """Finalize connection (save config, print info)"""
        # Save configuration (including address)
        if self.roon.token:
            need_save = (
                self.roon.token != self.token or
                self.roon.core_id != self.core_id or
                self.host != self.saved_host or
                self.port != self.saved_port
            )
            if need_save:
                self.token = self.roon.token
                self.core_id = self.roon.core_id
                self._save_config()

        if self.verbose:
            print(f"✓ Connected to Roon Core")
            print(f"  Core ID: {self.roon.core_id}")
            print(f"  Core name: {self.roon.core_name}")

    def find_zone_by_name(self, zone_name: str) -> Optional[Dict[str, Any]]:
        """
        Find zone by name

        Args:
            zone_name: zone name

        Returns:
            zone information, None if not found
        """
        try:
            zones = self.roon.zones
            if not zones:
                return None

            for zone_id, zone_data in zones.items():
                if zone_data.get('display_name', '') == zone_name:
                    return {'zone_id': zone_id, 'zone_data': zone_data}

            return None
        except Exception:
            return None

    def find_default_zone(self) -> Optional[Dict[str, Any]]:
        """
        Find default zone (with [roon] suffix)

        Returns:
            zone information, None if not found
        """
        try:
            zones = self.roon.zones

            if not zones:
                if self.verbose:
                    print("⚠  No zones found")
                return None

            # Find zone with [roon] suffix
            roon_zones = []
            for zone_id, zone_data in zones.items():
                zone_name = zone_data.get('display_name', '')
                if zone_name.lower().endswith('[roon]'):
                    roon_zones.append((zone_id, zone_data))

            if not roon_zones:
                if self.verbose:
                    print(f"⚠  No zones with '[roon]' suffix found")
                    print(f"  Available zones:")
                    for zone_id, zone_data in zones.items():
                        print(f"    - {zone_data.get('display_name', 'Unknown')}")
                return None

            # Return first matching zone
            zone_id, zone_data = roon_zones[0]
            if self.verbose:
                print(f"✓ Found default zone: {zone_data.get('display_name')}")

            return {'zone_id': zone_id, 'zone_data': zone_data}

        except Exception as e:
            if self.verbose:
                print(f"❌ Failed to find zone: {e}")
            return None

    def get_current_zone(self) -> Optional[Dict[str, Any]]:
        """
        Get current zone

        Priority:
        1. saved selected_zone from config
        2. zone with [roon] suffix
        """
        # If saved zone exists, try using it first
        if self.selected_zone:
            zone = self.find_zone_by_name(self.selected_zone)
            if zone:
                return zone
            else:
                if self.verbose:
                    print(f"⚠  Saved zone '{self.selected_zone}' unavailable, trying default zone")

        # Fall back to default zone
        return self.find_default_zone()

    def set_zone(self, zone_name: str) -> Dict[str, Any]:
        """
        Set current zone

        Args:
            zone_name: zone name

        Returns:
            operation result
        """
        # Verify zone exists
        zone = self.find_zone_by_name(zone_name)
        if not zone:
            available = self.list_zones()
            return {
                "success": False,
                "message": f"Zone '{zone_name}' not found",
                "available_zones": available
            }

        # Save to config
        self.selected_zone = zone_name
        self._save_config()

        return {
            "success": True,
            "message": f"Switched to zone: {zone_name}",
            "zone": zone_name
        }

    def _get_track_info(self, zone: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get current track info for zone

        Args:
            zone: zone information dictionary

        Returns:
            track information dictionary
        """
        try:
            state = zone['zone_data']
            now_playing = state.get('now_playing', {})

            return {
                "track": now_playing.get('two_line', {}).get('line1', 'Unknown'),
                "artist": now_playing.get('two_line', {}).get('line2', 'Unknown'),
                "album": now_playing.get('three_line', {}).get('line1', 'Unknown'),
            }
        except Exception:
            return {
                "track": "Unknown",
                "artist": "Unknown",
                "album": "Unknown"
            }

    def play(self) -> Dict[str, Any]:
        """Play"""
        zone = self.get_current_zone()
        if not zone:
            return {"success": False, "message": "Muspi zone not found"}

        try:
            self.roon.playback_control(zone['zone_id'], control='play')

            # Wait for state update
            time.sleep(0.3)

            # Get latest zone state
            zone = self.get_current_zone()
            track_info = self._get_track_info(zone) if zone else {}

            return {
                "success": True,
                "message": f"Started playing",
                "zone": zone['zone_data'].get('display_name'),
                **track_info
            }
        except Exception as e:
            return {"success": False, "message": f"Play failed: {e}"}

    def pause(self) -> Dict[str, Any]:
        """Pause"""
        zone = self.get_current_zone()
        if not zone:
            return {"success": False, "message": "Muspi zone not found"}

        try:
            self.roon.playback_control(zone['zone_id'], control='pause')
            return {
                "success": True,
                "message": f"Paused",
                "zone": zone['zone_data'].get('display_name')
            }
        except Exception as e:
            return {"success": False, "message": f"Pause failed: {e}"}

    def play_pause(self) -> Dict[str, Any]:
        """Toggle play/pause"""
        zone = self.get_current_zone()
        if not zone:
            return {"success": False, "message": "Muspi zone not found"}

        try:
            self.roon.playback_control(zone['zone_id'], control='playpause')
            return {
                "success": True,
                "message": f"Toggled play/pause",
                "zone": zone['zone_data'].get('display_name')
            }
        except Exception as e:
            return {"success": False, "message": f"Toggle failed: {e}"}

    def previous(self, threshold_seconds: float = 3.0) -> Dict[str, Any]:
        """
        Previous track

        If current track has been playing for more than threshold_seconds, will seek to beginning first
        """
        zone = self.get_current_zone()
        if not zone:
            return {"success": False, "message": "Muspi zone not found"}

        try:
            # Check current playback position
            now_playing = zone['zone_data'].get('now_playing', {})
            seek_position = now_playing.get('seek_position') or 0  # milliseconds

            # If playback exceeds threshold, seek to beginning first
            if seek_position > threshold_seconds * 1000:
                # Seek to track beginning
                self.roon.seek(zone['zone_id'], 0)
                time.sleep(0.2)

            # Switch to previous track
            self.roon.playback_control(zone['zone_id'], control='previous')

            # Wait for state update
            time.sleep(0.3)

            # Get latest zone state
            zone = self.get_current_zone()
            track_info = self._get_track_info(zone) if zone else {}

            return {
                "success": True,
                "message": f"Switched to previous track",
                "zone": zone['zone_data'].get('display_name'),
                **track_info
            }
        except Exception as e:
            return {"success": False, "message": f"Previous track failed: {e}"}

    def next(self) -> Dict[str, Any]:
        """Next track"""
        zone = self.get_current_zone()
        if not zone:
            return {"success": False, "message": "Muspi zone not found"}

        try:
            self.roon.playback_control(zone['zone_id'], control='next')

            # Wait for state update
            time.sleep(0.3)

            # Get latest zone state
            zone = self.get_current_zone()
            track_info = self._get_track_info(zone) if zone else {}

            return {
                "success": True,
                "message": f"Switched to next track",
                "zone": zone['zone_data'].get('display_name'),
                **track_info
            }
        except Exception as e:
            return {"success": False, "message": f"Next track failed: {e}"}

    def get_current_track(self) -> Dict[str, Any]:
        """Get current playing track info"""
        zone = self.get_current_zone()
        if not zone:
            return {"success": False, "message": "Muspi zone not found"}

        try:
            # Zone state is already included in zone_data
            state = zone['zone_data']

            if not state:
                return {
                    "success": False,
                    "message": "Cannot get playback state"
                }

            # Extract track info
            now_playing = state.get('now_playing', {})
            track_info = {
                "success": True,
                "is_playing": state.get('state') == 'playing',
                "zone": zone['zone_data'].get('display_name'),
                "track": now_playing.get('two_line', {}).get('line1', 'Unknown'),
                "artist": now_playing.get('two_line', {}).get('line2', 'Unknown'),
                "album": now_playing.get('three_line', {}).get('line1', 'Unknown'),
                "seek_position": now_playing.get('seek_position', 0),
                "length": now_playing.get('length', 0),
            }

            return track_info

        except Exception as e:
            return {"success": False, "message": f"Failed to get track info: {e}"}

    def list_zones(self) -> List[str]:
        """List all zones"""
        try:
            zones = self.roon.zones
            zone_names = []
            for zone_id, zone_data in zones.items():
                zone_names.append(zone_data.get('display_name', 'Unknown'))
            return zone_names
        except Exception as e:
            return [f"Failed to get zones: {e}"]

    def disconnect(self) -> None:
        """Disconnect"""
        if self.roon:
            self.roon.stop()
            if self.verbose:
                print("✓ Disconnected from Roon")


def main():
    """Command line test entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Roon Player Controller')
    parser.add_argument('command', nargs='?', default='status',
                        choices=['play', 'pause', 'prev', 'next', 'status', 'zones', 'switch'],
                        help='command')
    parser.add_argument('zone_name', nargs='?', default=None,
                        help='zone name (for switch command)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='show detailed logs')
    parser.add_argument('-H', '--host', help='Roon Core host address')

    args = parser.parse_args()

    # Create controller
    try:
        controller = RoonController(host=args.host, verbose=args.verbose)
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return 1

    # Execute command
    result = None
    if args.command == 'play':
        result = controller.play()
    elif args.command == 'pause':
        result = controller.pause()
    elif args.command == 'prev':
        result = controller.previous()
    elif args.command == 'next':
        result = controller.next()
    elif args.command == 'status':
        result = controller.get_current_track()
    elif args.command == 'zones':
        zones = controller.list_zones()
        current_zone = controller.selected_zone
        print("\nAvailable zones:")
        for zone in zones:
            if zone == current_zone:
                print(f"  * {zone} (current)")
            else:
                print(f"  - {zone}")
        if not current_zone:
            print("\n  (No zone set, will use default zone with [roon] suffix)")
        result = {"success": True, "zones": zones, "current_zone": current_zone}
    elif args.command == 'switch':
        if not args.zone_name:
            zones = controller.list_zones()
            print("\n❌ Please specify a zone name")
            print("\nUsage: python roon_controller.py switch \"zone name\"")
            print("\nAvailable zones:")
            for zone in zones:
                print(f"  - {zone}")
            result = {"success": False, "message": "No zone name specified"}
        else:
            result = controller.set_zone(args.zone_name)

    # Display result
    if result and isinstance(result, dict):
        if result.get('success'):
            if args.command == 'status':
                # Format and display track info
                print(f"\n🎵 Currently playing:")
                print(f"  Zone: {result.get('zone')}")
                print(f"  Status: {'Playing' if result.get('is_playing') else 'Paused'}")
                print(f"  Track: {result.get('track')}")
                print(f"  Artist: {result.get('artist')}")
                print(f"  Album: {result.get('album')}")

                # Calculate progress
                seek = result.get('seek_position', 0) / 1000
                length = result.get('length', 0) / 1000
                if length > 0:
                    progress = (seek / length) * 100
                    print(f"  Progress: {int(seek)}s / {int(length)}s ({progress:.1f}%)")
            elif args.command == 'zones':
                pass  # Already handled above
            elif args.command in ('play', 'prev', 'next'):
                # Display operation result and track info
                print(f"\n✅ {result.get('message')}")
                if result.get('track'):
                    print(f"  Track: {result.get('track')}")
                    print(f"  Artist: {result.get('artist')}")
                    print(f"  Album: {result.get('album')}")
            else:
                print(f"\n✅ {result.get('message')}")
        else:
            print(f"\n❌ {result.get('message')}")
            if result.get('available_zones'):
                print("\nAvailable zones:")
                for zone in result.get('available_zones'):
                    print(f"  - {zone}")

    # Cleanup
    controller.disconnect()
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
