#!/usr/bin/env python3
"""
Apple TV CLI - Control via pyatv

Usage:
    appletv.py status         Now playing + device state
    appletv.py playing        What's currently playing
    appletv.py play           Play/resume
    appletv.py pause          Pause
    appletv.py stop           Stop playback
    appletv.py next           Next track/chapter
    appletv.py prev           Previous track/chapter
    appletv.py menu           Press menu button
    appletv.py home           Go to home screen
    appletv.py select         Press select/OK
    appletv.py up             Navigate up
    appletv.py down           Navigate down
    appletv.py left           Navigate left
    appletv.py right          Navigate right
    appletv.py volume_up      Volume up
    appletv.py volume_down    Volume down
    appletv.py app <name>     Launch app by name
    appletv.py apps           List installed apps
    appletv.py turn_on        Turn on (wake)
    appletv.py turn_off       Turn off (sleep)
    appletv.py power          Toggle power state
    appletv.py scan           Scan for Apple TVs

Configuration:
    ~/clawd/config/appletv.json or ~/.config/clawdbot/appletv.json
"""

import sys
import os
import json
import asyncio
from pathlib import Path

CONFIG_PATHS = [
    Path.home() / "clawd" / "config" / "appletv.json",
    Path.home() / ".config" / "clawdbot" / "appletv.json",
]

# Find atvremote binary
ATVREMOTE = Path.home() / ".local" / "bin" / "atvremote"
if not ATVREMOTE.exists():
    ATVREMOTE = "atvremote"  # Hope it's in PATH

def get_config():
    """Load config from file."""
    for config_path in CONFIG_PATHS:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
    return None

def require_config():
    """Get config or exit with helpful message."""
    config = get_config()
    if not config:
        print("❌ No Apple TV configured!")
        print()
        print("Run pairing first:")
        print("  atvremote scan")
        print("  atvremote --id <ID> --protocol companion pair")
        print("  atvremote --id <ID> --protocol airplay pair")
        print()
        print("Then create ~/clawd/config/appletv.json:")
        print('  {"id": "...", "credentials": {"companion": "...", "airplay": "..."}}')
        sys.exit(1)
    return config

def run_atvremote(*args):
    """Run atvremote with credentials from config."""
    config = require_config()
    
    cmd = [str(ATVREMOTE), "--id", config["id"]]
    
    creds = config.get("credentials", {})
    if creds.get("companion"):
        cmd.extend(["--companion-credentials", creds["companion"]])
    if creds.get("airplay"):
        cmd.extend(["--airplay-credentials", creds["airplay"]])
    
    cmd.extend(args)
    
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

def cmd_status():
    """Show full status."""
    config = require_config()
    print(f"📺 {config.get('name', 'Apple TV')}")
    print()
    
    stdout, stderr, code = run_atvremote("playing")
    if code == 0 and stdout.strip():
        for line in stdout.strip().split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip()
                
                if key == "Device state":
                    emoji = {"Playing": "▶️", "Paused": "⏸️", "Stopped": "⏹️", "Idle": "💤"}.get(val, "❓")
                    print(f"{emoji} State: {val}")
                elif key == "Title":
                    print(f"🎬 Title: {val}")
                elif key == "Artist":
                    print(f"🎤 Artist: {val}")
                elif key == "Album":
                    print(f"💿 Album: {val}")
                elif key == "Position":
                    print(f"⏱️  Position: {val}")
                elif key == "Media type":
                    print(f"📀 Type: {val}")
    else:
        print("💤 Idle or unavailable")
        if stderr:
            print(f"   (Error: {stderr.strip()[:100]})")
    return 0

def cmd_playing():
    """Show what's playing."""
    stdout, stderr, code = run_atvremote("playing")
    if code == 0:
        print(stdout)
    else:
        print("❌ Could not get playing info")
        if stderr:
            print(stderr)
    return code

def cmd_simple(command, emoji, success_msg):
    """Run a simple command."""
    stdout, stderr, code = run_atvremote(command)
    if code == 0:
        print(f"{emoji} {success_msg}")
    else:
        print(f"❌ Failed: {stderr.strip() if stderr else 'Unknown error'}")
    return code

def cmd_app(app_name):
    """Launch an app."""
    stdout, stderr, code = run_atvremote("launch_app=" + app_name)
    if code == 0:
        print(f"🚀 Launching {app_name}")
    else:
        print(f"❌ Failed to launch {app_name}")
        if stderr:
            print(f"   {stderr.strip()}")
        print("\nTry 'appletv.py apps' to see available apps")
    return code

def cmd_apps():
    """List installed apps."""
    stdout, stderr, code = run_atvremote("app_list")
    if code == 0 and stdout.strip():
        print("📱 Installed Apps:\n")
        # Parse the app list - handle both newline-separated and comma-separated formats
        text = stdout.strip()
        # Split on "App:" to handle single-line format
        if text.count("App:") > 1 and text.count("\n") < text.count("App:"):
            entries = text.split("App:")
        else:
            entries = None

        if entries:
            for entry in entries:
                entry = entry.strip().strip(",").strip("-").strip()
                if entry:
                    # Extract name and bundle id
                    if "(" in entry and ")" in entry:
                        name = entry[:entry.rfind("(")].strip()
                        bundle = entry[entry.rfind("(")+1:entry.rfind(")")].strip()
                        print(f"  • {name}  ({bundle})")
                    else:
                        print(f"  • {entry}")
        else:
            for line in text.split('\n'):
                line = line.strip()
                if line.startswith("- App:"):
                    parts = line[6:].strip()
                    print(f"  • {parts}")
                elif line.startswith("App:"):
                    parts = line[4:].strip()
                    print(f"  • {parts}")
                elif line and not line.startswith("="):
                    print(f"  {line}")
    else:
        print("❌ Could not list apps")
    return code

def cmd_scan():
    """Scan for Apple TVs."""
    import subprocess
    print("🔍 Scanning for Apple TVs...\n")
    result = subprocess.run([str(ATVREMOTE), "scan"], capture_output=False)
    return result.returncode

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 0
    
    cmd = sys.argv[1].lower()
    
    simple_commands = {
        "play": ("play", "▶️", "Playing"),
        "pause": ("pause", "⏸️", "Paused"),
        "stop": ("stop", "⏹️", "Stopped"),
        "next": ("next", "⏭️", "Next"),
        "prev": ("previous", "⏮️", "Previous"),
        "previous": ("previous", "⏮️", "Previous"),
        "menu": ("menu", "📋", "Menu"),
        "home": ("home", "🏠", "Home"),
        "select": ("select", "✅", "Selected"),
        "ok": ("select", "✅", "Selected"),
        "up": ("up", "⬆️", "Up"),
        "down": ("down", "⬇️", "Down"),
        "left": ("left", "⬅️", "Left"),
        "right": ("right", "➡️", "Right"),
        "volume_up": ("volume_up", "🔊", "Volume up"),
        "volume_down": ("volume_down", "🔉", "Volume down"),
        "turn_on": ("turn_on", "📺", "Turned on"),
        "turn_off": ("turn_off", "💤", "Turned off"),
        "power": ("power", "⚡", "Power toggled"),
    }
    
    if cmd == "status":
        return cmd_status()
    elif cmd == "playing":
        return cmd_playing()
    elif cmd == "apps":
        return cmd_apps()
    elif cmd == "app" and len(sys.argv) > 2:
        return cmd_app(" ".join(sys.argv[2:]))
    elif cmd == "scan":
        return cmd_scan()
    elif cmd in simple_commands:
        atvremote_cmd, emoji, msg = simple_commands[cmd]
        return cmd_simple(atvremote_cmd, emoji, msg)
    else:
        print(f"❌ Unknown command: {cmd}")
        print(__doc__)
        return 1

if __name__ == "__main__":
    sys.exit(main())
