---
name: findmy-location
description: Track a shared contact's location via Apple Find My with street-level accuracy. Returns address, city, and context (home/work/out) by reading map landmarks. Supports configurable known locations and vision fallback for unknown places.
---

# Find My Location

Track shared contacts via Apple Find My with street-corner accuracy.

## Requirements

- **macOS** 13+ with Find My app
- **Python** 3.9+
- **iCloud account** signed in on your Mac (for Find My access)
- **Location sharing** enabled from the contact you want to track
- **peekaboo** - screen reading CLI ([GitHub](https://github.com/steipete/peekaboo))
- **Hammerspoon** (optional) - for reliable UI clicking ([hammerspoon.org](https://www.hammerspoon.org/))

## Prerequisites

### 1. iCloud & Find My Setup

Your Mac must be signed into an iCloud account with Find My enabled:
- System Settings → Apple ID → iCloud → Find My Mac (enabled)
- The person you want to track must share their location with this iCloud account via Find My

### 2. Install peekaboo

```bash
brew install steipete/tap/peekaboo
```

Grant **Accessibility** and **Screen Recording** permissions when prompted (System Settings → Privacy & Security).

### 3. Install Hammerspoon (optional but recommended)

Hammerspoon provides reliable clicking that works across all apps. Without it, clicks may occasionally go to the wrong window.

```bash
brew install hammerspoon
open -a Hammerspoon
```

Add to `~/.hammerspoon/init.lua`:
```lua
local server = hs.httpserver.new(false, false)
server:setPort(9090)
server:setCallback(function(method, path, headers, body)
    local data = body and hs.json.decode(body) or {}
    if path == "/click" then
        hs.eventtap.leftClick({x=data.x, y=data.y})
        return hs.json.encode({status="clicked", x=data.x, y=data.y}), 200, {}
    end
    return hs.json.encode({error="not found"}), 404, {}
end)
server:start()
```

Reload config (Hammerspoon menu → Reload Config), then create `~/.local/bin/hsclick`:
```bash
#!/bin/bash
curl -s -X POST localhost:9090/click -d "{\"x\":$2,\"y\":$3}"
chmod +x ~/.local/bin/hsclick
```

## Installation

```bash
git clone https://github.com/poiley/findmy-location.git
cd findmy-location
./install.sh
```

Or via ClawdHub:
```bash
clawdhub install findmy-location
```

## Configuration

Create `~/.config/findmy-location/config.json`:
```json
{
  "target": "John",
  "known_locations": [
    {
      "name": "home",
      "address": "123 Main St, City, ST",
      "markers": ["landmark near home"]
    },
    {
      "name": "work",
      "address": "456 Office Blvd, City, ST",
      "markers": ["landmark near work"]
    }
  ]
}
```

| Field | Description |
|-------|-------------|
| `target` | Contact name to track (optional - defaults to first shared contact) |
| `known_locations` | Array of places you want labeled with addresses |
| `markers` | Landmarks visible on the Find My map when at that location |

## Usage

```bash
findmy-location          # Human-readable output
findmy-location --json   # JSON output
```

### Example Output

```
123 Main St, City, ST (home) - Now
```

```json
{
  "person": "contact@email.com",
  "address": "Main St & 1st Ave",
  "city": "Anytown",
  "state": "WA",
  "status": "Now",
  "context": "out",
  "screenshot": "/tmp/findmy-12345.png",
  "needs_vision": false
}
```

| Field | Description |
|-------|-------------|
| `context` | `home`, `work`, `out`, or `unknown` |
| `needs_vision` | If `true`, use AI vision on screenshot to read street names |
| `screenshot` | Path to captured map image |

## How It Works

1. Opens Find My app and selects target contact
2. Captures map and reads accessibility data
3. Matches visible landmarks against configured known locations
4. Returns address and context, or flags for vision analysis

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Clicks go to wrong window | Install Hammerspoon (see prerequisites) |
| "No person found" | Ensure location sharing is enabled in Find My |
| Always shows `needs_vision: true` | Add markers for frequently visited places |
| Permission errors | Grant peekaboo Accessibility + Screen Recording access |

## License

MIT
