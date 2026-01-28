---
name: devialet
description: "Control Devialet Phantom speakers via HTTP API. Use for: play/pause, volume control, mute/unmute, source selection, and speaker status. Requires DOS 2.14+ firmware. Works with Phantom I, Phantom II, Phantom Reactor, and Dialog."
---

# Devialet Speaker Control

Control Devialet speakers (Phantom, Mania) over your local network with Spotify integration.

## Natural Language Commands

When the user says things like:
- **"Play Nines - Lick Shots on my speaker"** → Search and play via Spotify
- **"Set speaker volume to 40"** → Adjust volume
- **"Pause the music"** → Pause playback
- **"What's playing?"** → Check current track and status

## Setup

1. Find your speaker's IP address (check router or Devialet app)
2. Set the `DEVIALET_IP` environment variable, or add to `TOOLS.md`:
   ```
   ## Devialet Speaker
   - IP: 192.168.x.x
   ```
3. For Spotify integration: install Spotify desktop app, playerctl, and xdotool

## Quick Usage

```bash
# Set your speaker IP
export DEVIALET_IP="192.168.x.x"

# Play a song (search and play)
./scripts/play-on-devialet.sh "Drake - God's Plan"

# Play by Spotify URI
./scripts/play-on-devialet.sh spotify:track:4YZNJOA9d8wiO5ELNY5WxC

# Pause / Resume
./scripts/play-on-devialet.sh pause
./scripts/play-on-devialet.sh resume

# Volume
./scripts/play-on-devialet.sh volume 50

# Status
./scripts/play-on-devialet.sh status
```

## Requirements

- **Devialet speaker** with DOS 2.14+ or SDOS 1.3+ firmware
- **Spotify integration** (optional):
  - Spotify desktop app running and logged in
  - `playerctl` and `xdotool` installed (`sudo apt install playerctl xdotool`)
  - Speaker set as Spotify Connect device (select once in Spotify app)

## How It Works

1. Searches for track via Spotify desktop app (D-Bus/MPRIS)
2. Opens track URI in Spotify
3. Spotify Connect streams to Devialet
4. Devialet API controls playback/volume

## Direct Devialet API

For non-Spotify control (replace `$DEVIALET_IP` with your speaker's IP):

```bash
# Volume (0-100)
curl -X POST -H "Content-Type: application/json" \
  -d '{"volume": 50}' \
  "http://$DEVIALET_IP/ipcontrol/v1/systems/current/sources/current/soundControl/volume"

# Play/Pause
curl -X POST "http://$DEVIALET_IP/ipcontrol/v1/groups/current/sources/current/playback/play"
curl -X POST "http://$DEVIALET_IP/ipcontrol/v1/groups/current/sources/current/playback/pause"

# Mute/Unmute
curl -X POST "http://$DEVIALET_IP/ipcontrol/v1/groups/current/sources/current/playback/mute"
curl -X POST "http://$DEVIALET_IP/ipcontrol/v1/groups/current/sources/current/playback/unmute"

# Get status
curl -s "http://$DEVIALET_IP/ipcontrol/v1/devices/current" | jq .
```

## Supported Models

- Phantom I, Phantom II, Phantom Reactor (DOS 2.14+)
- Dialog
- Mania (SDOS 1.3+)

## API Reference

See `references/api.md` for complete endpoint documentation.
