---
name: appletv
version: 1.0.0
description: Control Apple TV via pyatv. Use for play/pause, navigation, volume, launching apps, power control, and checking what's playing. Triggers on "Apple TV", "TV", "what's playing", "pause TV", "play TV", "turn off TV".
license: MIT
---

# Apple TV Control

Control Apple TV via the pyatv library.

## Requirements

```bash
pipx install pyatv --python python3.11
```

> **Note:** pyatv requires Python ≤3.13. Python 3.14+ has breaking asyncio changes. Use `--python python3.11` or `python3.13` with pipx.

## Configuration

Config file at `~/clawd/config/appletv.json`:

```json
{
  "name": "Living Room",
  "id": "DEVICE_ID",
  "ip": "192.168.x.x",
  "credentials": {
    "companion": "...",
    "airplay": "..."
  }
}
```

### First-Time Pairing

```bash
# Find your Apple TV
atvremote scan

# Pair Companion protocol (required)
atvremote --id <DEVICE_ID> --protocol companion pair

# Pair AirPlay protocol (for media)
atvremote --id <DEVICE_ID> --protocol airplay pair
```

Save the credentials to the config file.

## Quick Commands

### Status & Playing
```bash
scripts/appletv.py status     # Full status with now playing
scripts/appletv.py playing    # What's currently playing
```

### Playback Control
```bash
scripts/appletv.py play       # Play/resume
scripts/appletv.py pause      # Pause
scripts/appletv.py stop       # Stop
scripts/appletv.py next       # Next track/chapter
scripts/appletv.py prev       # Previous
```

### Navigation
```bash
scripts/appletv.py up         # Navigate up
scripts/appletv.py down       # Navigate down
scripts/appletv.py left       # Navigate left
scripts/appletv.py right      # Navigate right
scripts/appletv.py select     # Press select/OK
scripts/appletv.py menu       # Menu button
scripts/appletv.py home       # Home screen
```

### Volume
```bash
scripts/appletv.py volume_up
scripts/appletv.py volume_down
```

### Power
```bash
scripts/appletv.py turn_on    # Wake from sleep
scripts/appletv.py turn_off   # Put to sleep
scripts/appletv.py power      # Toggle
```

### Apps
```bash
scripts/appletv.py apps       # List installed apps
scripts/appletv.py app Netflix
scripts/appletv.py app YouTube
scripts/appletv.py app "Disney+"
```

### Discovery
```bash
scripts/appletv.py scan       # Find Apple TVs on network
```

## Example Interactions

- "What's playing on the TV?" → `scripts/appletv.py status`
- "Pause the TV" → `scripts/appletv.py pause`
- "Turn off the Apple TV" → `scripts/appletv.py turn_off`
- "Open Netflix on TV" → `scripts/appletv.py app Netflix`
