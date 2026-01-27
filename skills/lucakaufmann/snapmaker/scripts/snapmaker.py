#!/usr/bin/env python3
"""
Snapmaker U1 CLI - Control via Moonraker API

Usage:
    snapmaker.py status          Full status (temps, progress, position)
    snapmaker.py temps           Show all temperatures
    snapmaker.py filament        Show filament info (colors, types, sensors)
    snapmaker.py monitor         Continuous status updates
    snapmaker.py pause           Pause current print
    snapmaker.py resume          Resume paused print
    snapmaker.py cancel          Cancel current print
    snapmaker.py files           List gcode files
    snapmaker.py gcode <CMD>     Send G-code command

Environment:
    SNAPMAKER_IP    Printer IP address (overrides config file)
"""

import sys
import os
import socket
import json
import time
from datetime import timedelta, datetime
from pathlib import Path

CONFIG_PATHS = [
    Path.home() / "clawd" / "config" / "snapmaker.json",
    Path.home() / ".config" / "clawdbot" / "snapmaker.json",
]
DEFAULT_PORT = 80

def get_config():
    """Load config from file or environment."""
    # Environment override takes priority
    if os.environ.get("SNAPMAKER_IP"):
        return {
            "ip": os.environ["SNAPMAKER_IP"],
            "port": int(os.environ.get("SNAPMAKER_PORT", DEFAULT_PORT))
        }
    
    # Try config files
    for config_path in CONFIG_PATHS:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    if "ip" in config:
                        config.setdefault("port", DEFAULT_PORT)
                        return config
            except (json.JSONDecodeError, IOError):
                pass
    
    # No config found
    return None

def get_ip():
    config = get_config()
    if not config:
        print("❌ No printer configured!")
        print()
        print("Create ~/clawd/config/snapmaker.json:")
        print('  {"ip": "192.168.x.x"}')
        print()
        print("Or set environment variable:")
        print("  export SNAPMAKER_IP=192.168.x.x")
        sys.exit(1)
    return config["ip"]

def get_port():
    config = get_config()
    return config["port"] if config else DEFAULT_PORT

def http_request(method, path, body=None):
    """Make HTTP request to Moonraker API."""
    ip = get_ip()
    port = get_port()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        sock.connect((ip, port))
        
        headers = f"{method} {path} HTTP/1.1\r\nHost: {ip}\r\nConnection: close\r\n"
        if body:
            headers += f"Content-Type: application/json\r\nContent-Length: {len(body)}\r\n"
        headers += "\r\n"
        
        sock.send(headers.encode())
        if body:
            sock.send(body.encode())
        
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        
        sock.close()
        
        # Parse response
        parts = response.split(b"\r\n\r\n", 1)
        if len(parts) < 2:
            return None
        
        return json.loads(parts[1])
    
    except socket.error as e:
        print(f"❌ Connection failed: {e}")
        print(f"   Check that printer is on and IP is correct ({ip})")
        sys.exit(1)
    except json.JSONDecodeError:
        return None

def get_status():
    """Get full printer status including all 4 extruders."""
    query = "extruder&extruder1&extruder2&extruder3&heater_bed&fan&temperature_sensor%20cavity&print_stats&virtual_sdcard&display_status&toolhead"
    data = http_request("GET", f"/printer/objects/query?{query}")
    if not data or "result" not in data:
        return None
    return data["result"]["status"]

def get_filament_info():
    """Get filament RFID data and sensor status."""
    query = "filament_detect&filament_motion_sensor%20e0_filament&filament_motion_sensor%20e1_filament&filament_motion_sensor%20e2_filament&filament_motion_sensor%20e3_filament"
    data = http_request("GET", f"/printer/objects/query?{query}")
    if not data or "result" not in data:
        return None
    return data["result"]["status"]

def rgb_int_to_hex(rgb_int):
    """Convert RGB integer to hex color string."""
    r = (rgb_int >> 16) & 0xFF
    g = (rgb_int >> 8) & 0xFF
    b = rgb_int & 0xFF
    return f"#{r:02X}{g:02X}{b:02X}"

def get_color_emoji(rgb_int):
    """Return approximate color emoji based on RGB value."""
    if rgb_int == 16777215:  # White
        return "⚪"
    r = (rgb_int >> 16) & 0xFF
    g = (rgb_int >> 8) & 0xFF
    b = rgb_int & 0xFF
    
    # Simple heuristics for common colors
    if r > 200 and g < 100 and b < 100:
        return "🔴"
    if r > 200 and g > 150 and b < 100:
        return "🟠"
    if r > 200 and g > 200 and b < 100:
        return "🟡"
    if r < 100 and g > 200 and b < 100:
        return "🟢"
    if r < 100 and g < 100 and b > 200:
        return "🔵"
    if r > 150 and g < 100 and b > 150:
        return "🟣"
    if r < 80 and g < 80 and b < 80:
        return "⚫"
    if r > 200 and g > 200 and b > 200:
        return "⚪"
    if r > 150 and g > 100 and b < 100:
        return "🟤"
    return "🔘"

def format_temp(temp, target):
    """Format temperature with target."""
    if target > 0:
        return f"{temp:.1f}°C → {target:.0f}°C"
    return f"{temp:.1f}°C"

def cmd_status():
    """Show full printer status."""
    status = get_status()
    if not status:
        print("❌ Failed to get status")
        return 1
    
    ps = status.get("print_stats", {})
    sd = status.get("virtual_sdcard", {})
    bed = status.get("heater_bed", {})
    th = status.get("toolhead", {})
    fan = status.get("fan", {})
    cavity = status.get("temperature_sensor cavity", {})
    
    state = ps.get("state", "unknown")
    state_emoji = {"standby": "💤", "printing": "🖨️", "paused": "⏸️", "complete": "✅", "error": "❌"}.get(state, "❓")
    
    print(f"{state_emoji} Status: {state.upper()}")
    print()
    
    # All 4 extruders
    print("🔥 Nozzles:")
    for i, ext_name in enumerate(["extruder", "extruder1", "extruder2", "extruder3"]):
        ext = status.get(ext_name, {})
        temp = ext.get("temperature", 0)
        target = ext.get("target", 0)
        ext_state = ext.get("state", "?")
        
        # Emoji based on state
        if ext_state == "ACTIVATE":
            icon = "🟢"
        elif ext_state == "PARKED":
            icon = "⚪"
        else:
            icon = "🔵"
        
        print(f"   {icon} T{i}: {format_temp(temp, target):20} [{ext_state}]")
    
    print()
    print(f"🛏️  Bed:    {format_temp(bed.get('temperature', 0), bed.get('target', 0))}")
    
    if cavity:
        print(f"🌡️  Cavity: {cavity.get('temperature', 0):.1f}°C")
    
    print(f"💨 Fan:    {fan.get('speed', 0)*100:.0f}%")
    
    # Print info
    if state == "printing" or ps.get("filename"):
        print()
        print(f"📁 File: {ps.get('filename', 'N/A')}")
        
        # Use display_status progress (accounts for layer timing) over virtual_sdcard (file position)
        ds = status.get("display_status", {})
        progress = ds.get("progress", sd.get("progress", 0)) * 100
        duration = ps.get("print_duration", 0)
        
        # Layer info
        info = ps.get("info", {})
        current_layer = info.get("current_layer", 0)
        total_layer = info.get("total_layer", 0)
        if total_layer > 0:
            print(f"📊 Progress: {progress:.1f}% (layer {current_layer}/{total_layer})")
        else:
            print(f"📊 Progress: {progress:.1f}%")
        
        print(f"⏱️  Elapsed: {str(timedelta(seconds=int(duration)))}")
        
        # Estimate remaining using display progress
        if progress > 0:
            total_est = duration / (progress / 100)
            remaining = total_est - duration
            print(f"⏳ Remaining: ~{str(timedelta(seconds=int(remaining)))}")
            
            # Calculate ETA
            eta = datetime.now() + timedelta(seconds=remaining)
            print(f"🏁 ETA: {eta.strftime('%a %b %d, %H:%M')}")
    
    # Position
    pos = th.get("position", [0, 0, 0, 0])
    print()
    print(f"📍 Position: X={pos[0]:.1f} Y={pos[1]:.1f} Z={pos[2]:.1f}")
    
    return 0

def cmd_temps():
    """Show all temperatures."""
    status = get_status()
    if not status:
        print("❌ Failed to get status")
        return 1
    
    bed = status.get("heater_bed", {})
    cavity = status.get("temperature_sensor cavity", {})
    
    print("🔥 Nozzle Temperatures:")
    for i, ext_name in enumerate(["extruder", "extruder1", "extruder2", "extruder3"]):
        ext = status.get(ext_name, {})
        temp = ext.get("temperature", 0)
        target = ext.get("target", 0)
        ext_state = ext.get("state", "?")
        power = ext.get("power", 0) * 100
        
        active = "●" if ext_state == "ACTIVATE" else "○"
        print(f"   {active} T{i}: {temp:6.1f}°C (target: {target:5.0f}°C) power: {power:4.1f}% [{ext_state}]")
    
    print()
    print(f"🛏️  Bed:    {bed.get('temperature', 0):6.1f}°C (target: {bed.get('target', 0):5.0f}°C) power: {bed.get('power', 0)*100:4.1f}%")
    
    if cavity:
        print(f"🌡️  Cavity: {cavity.get('temperature', 0):6.1f}°C")
    
    return 0

def cmd_filament():
    """Show filament information from RFID tags and sensors."""
    info = get_filament_info()
    if not info:
        print("❌ Failed to get filament info")
        return 1
    
    filament_detect = info.get("filament_detect", {})
    slots = filament_detect.get("info", [])
    
    print("🎨 Filament Slots:\n")
    
    for i, slot in enumerate(slots):
        vendor = slot.get("VENDOR", "NONE")
        sensor_key = f"filament_motion_sensor e{i}_filament"
        sensor = info.get(sensor_key, {})
        detected = sensor.get("filament_detected", False)
        
        if vendor == "NONE":
            # Empty or non-RFID filament
            status = "✅ loaded" if detected else "❌ empty"
            print(f"   Slot {i}: No RFID tag ({status})")
            if detected:
                print(f"           ⚠️  Third-party filament (no data)")
            print()
            continue
        
        # Has RFID data
        manufacturer = slot.get("MANUFACTURER", "?")
        main_type = slot.get("MAIN_TYPE", "?")
        sub_type = slot.get("SUB_TYPE", "")
        rgb = slot.get("RGB_1", 16777215)
        weight = slot.get("WEIGHT", 0)
        hotend_min = slot.get("HOTEND_MIN_TEMP", 0)
        hotend_max = slot.get("HOTEND_MAX_TEMP", 0)
        bed_temp = slot.get("BED_TEMP", 0)
        official = slot.get("OFFICIAL", False)
        
        color_hex = rgb_int_to_hex(rgb)
        color_emoji = get_color_emoji(rgb)
        
        filament_name = main_type
        if sub_type and sub_type != "generic":
            filament_name = f"{main_type} {sub_type}"
        
        status = "✅" if detected else "⚠️"
        official_tag = " [Official]" if official else ""
        
        print(f"   Slot {i}: {color_emoji} {filament_name} ({manufacturer}){official_tag}")
        print(f"           Color: {color_hex}")
        print(f"           Temps: {hotend_min}-{hotend_max}°C nozzle, {bed_temp}°C bed")
        print(f"           Weight: {weight}g")
        print(f"           Sensor: {status} {'detected' if detected else 'not detected'}")
        print()
    
    return 0

def cmd_monitor():
    """Continuous status monitoring."""
    print("📡 Monitoring printer (Ctrl+C to stop)...\n")
    try:
        while True:
            status = get_status()
            if status:
                ps = status.get("print_stats", {})
                sd = status.get("virtual_sdcard", {})
                bed = status.get("heater_bed", {})
                
                # Find active extruder
                active_ext = None
                active_temp = 0
                for i, ext_name in enumerate(["extruder", "extruder1", "extruder2", "extruder3"]):
                    ext = status.get(ext_name, {})
                    if ext.get("state") == "ACTIVATE":
                        active_ext = i
                        active_temp = ext.get("temperature", 0)
                        break
                
                state = ps.get("state", "?")
                progress = sd.get("progress", 0) * 100
                duration = ps.get("print_duration", 0)
                
                line = f"\r[{state.upper():8}] "
                line += f"{progress:5.1f}% | "
                if active_ext is not None:
                    line += f"T{active_ext}: {active_temp:5.1f}°C | "
                line += f"Bed: {bed.get('temperature', 0):5.1f}°C | "
                line += f"{str(timedelta(seconds=int(duration)))}"
                
                print(line + "    ", end="", flush=True)
            
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\n👋 Stopped monitoring")
    return 0

def cmd_pause():
    """Pause current print."""
    print("⏸️  Pausing print...")
    result = http_request("POST", "/printer/print/pause")
    if result:
        print("✅ Print paused")
        return 0
    print("❌ Failed to pause")
    return 1

def cmd_resume():
    """Resume paused print."""
    print("▶️  Resuming print...")
    result = http_request("POST", "/printer/print/resume")
    if result:
        print("✅ Print resumed")
        return 0
    print("❌ Failed to resume")
    return 1

def cmd_cancel():
    """Cancel current print."""
    print("🛑 Cancelling print...")
    result = http_request("POST", "/printer/print/cancel")
    if result:
        print("✅ Print cancelled")
        return 0
    print("❌ Failed to cancel")
    return 1

def cmd_files():
    """List gcode files."""
    data = http_request("GET", "/server/files/list")
    if not data or "result" not in data:
        print("❌ Failed to list files")
        return 1
    
    files = data["result"]
    print(f"📁 Found {len(files)} files:\n")
    for f in files[:20]:
        name = f.get("path", f.get("filename", "?"))
        size_mb = f.get("size", 0) / 1024 / 1024
        print(f"  • {name} ({size_mb:.1f} MB)")
    
    if len(files) > 20:
        print(f"\n  ... and {len(files) - 20} more")
    return 0

def cmd_gcode(command):
    """Send G-code command."""
    print(f"📤 Sending: {command}")
    body = json.dumps({"script": command})
    result = http_request("POST", "/printer/gcode/script", body)
    if result:
        print("✅ Command sent")
        return 0
    print("❌ Failed to send command")
    return 1

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 0
    
    cmd = sys.argv[1].lower()
    
    commands = {
        "status": cmd_status,
        "temps": cmd_temps,
        "filament": cmd_filament,
        "monitor": cmd_monitor,
        "pause": cmd_pause,
        "resume": cmd_resume,
        "cancel": cmd_cancel,
        "files": cmd_files,
    }
    
    if cmd == "gcode" and len(sys.argv) > 2:
        return cmd_gcode(" ".join(sys.argv[2:]))
    
    if cmd in commands:
        return commands[cmd]()
    
    print(f"❌ Unknown command: {cmd}")
    print(__doc__)
    return 1

if __name__ == "__main__":
    sys.exit(main())
