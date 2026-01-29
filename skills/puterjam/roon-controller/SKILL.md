---
name: roon-controller
description: Control Roon music player through Roon API with automatic Core discovery and zone filtering. Supports play/pause, next/previous track, and current track query. Automatically finds Muspi zones. Supports Chinese commands.
---

# Roon Control Skill

Control the Roon music player with Chinese command support.

## Quick Start

### Install Dependencies

```bash
pip install roonapi
```

### Usage Examples

```python
from roon_controller import RoonController

# Create controller (token will be saved automatically)
controller = RoonController(verbose=True)

# Play/Pause
result = controller.play_pause()

# Next track
result = controller.next()

# Get current track
track_info = controller.get_current_track()
print(f"Now playing: {track_info['track']}")
```

## Core Features

### 1. Automatic Discovery and Connection
- Automatic Roon Core discovery
- Token automatically saved to `~/clawd/roon_config.json`
- Auto-reconnect after restart, no re-authorization needed

### 2. Zone Selection and Switching
- Supports switching between any available zone
- Selected zone is saved in config and persists across restarts
- If no zone is selected, defaults to zones ending with "[roon]"
- Use `set_zone()` to switch zones programmatically

**Switch Zone**
```python
result = controller.set_zone("Living Room")
# {"success": True, "message": "Switched to zone: Living Room", "zone": "Living Room"}
```

**Get Current Zone**
```python
zone = controller.get_current_zone()
# Returns zone info dict with zone_id and zone_data
```

### 3. Playback Control

**Play**
```python
result = controller.play()
# {"success": True, "message": "Playback started", "zone": "Living Room Muspi"}
```

**Pause**
```python
result = controller.pause()
# {"success": True, "message": "Paused", "zone": "Living Room Muspi"}
```

**Play/Pause Toggle**
```python
result = controller.play_pause()
```

**Previous Track**
```python
result = controller.previous()
```

**Next Track**
```python
result = controller.next()
```

### 4. Get Current Track

```python
track_info = controller.get_current_track()
# Returns:
# {
#   "success": True,
#   "is_playing": True,
#   "zone": "Living Room Muspi",
#   "track": "Bohemian Rhapsody",
#   "artist": "Queen",
#   "album": "A Night at the Opera",
#   "seek_position": 12345,  # milliseconds
#   "length": 354000        # milliseconds
# }
```

### 5. List All Zones

```python
zones = controller.list_zones()
# ["Living Room Muspi", "Kitchen", "Bedroom"]
```

## Command Line Tool

The script can be used as a command line tool:

```bash
# Play
python roon_controller.py play

# Pause
python roon_controller.py pause

# Previous track
python roon_controller.py prev

# Next track
python roon_controller.py next

# View current track
python roon_controller.py status

# List all zones
python roon_controller.py zones -v

# switch zone
python roon_controller.py switch zonename
```

## Chinese Command Support

The skill supports the following Chinese trigger words:

| Command | Meaning | Example |
|---------|---------|---------|
| 音乐播放 / 播放音乐 | Start playback | "音乐播放" |
| 暂停 / 暂停播放 | Pause playback | "暂停一下" |
| 下一曲 / 切歌 | Next track | "下一曲" |
| 上一曲 | Previous track | "上一曲" |
| 当前曲目 / 正在放什么 | View current track | "当前曲目" |

## Error Handling

All methods return a unified dictionary structure:

```python
{
    "success": True/False,
    "message": "Operation result description",
    "zone": "Zone name (optional)"
}
```

### Common Errors

- **Muspi zone not found**: Check if the Roon zone name ends with "muspi"
- **Failed to connect to Roon**: Ensure Roon Core is running and network-accessible
- **Token load failed**: First run requires authorization, ensure authorization completes successfully

## Notes

1. **First Run**: Extension authorization required in Roon, check for the extension authorization prompt in Roon interface
2. **Zone Naming**: Muspi zone names must end with "muspi" (case-insensitive)
3. **Token Storage**: Token is saved in `~/clawd/roon_config.json`, ensure secure file permissions
4. **Network Requirements**: The device running the script must be on the same network as Roon Core

## Technical Details

### Dependencies
- `roonapi>=0.1.6`: Official Roon API Python library

### Token Management
- Token storage path: `~/clawd/roon_config.json`
- Auto-load: Automatically loaded on each startup
- Auto-save: Automatically saved on first authorization or update

### Zone Finding Algorithm
```python
# Find all zones
zones = roon.zones

# Filter zones with muspi suffix
muspi_zones = [
    (zone_id, zone_data)
    for zone_id, zone_data in zones.items()
    if zone_data['display_name'].lower().endswith('muspi')
]

# Use the first matching zone
zone_id, zone_data = muspi_zones[0]
```
