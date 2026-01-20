---
name: holocube
description: Control GeekMagic HelloCubic-Lite holographic cube display with HoloClawd firmware. Supports drawing API, pomodoro timer with lobster mascot, GIF uploads, and procedural animations.
homepage: https://github.com/andrewjiang/HoloClawd-Open-Firmware
metadata: {"clawdbot":{"emoji":"🦞","os":["darwin","linux"]}}
triggers:
  - holocube
  - holo cube
  - holoclawd
  - cubic
  - geekmagic
  - display gif
  - cube animation
  - pomodoro
  - lobster timer
  - water tracker
  - hydration
  - drink water
---

# HoloCube Controller

Control the GeekMagic HelloCubic-Lite with HoloClawd firmware via REST API.

**Firmware:** https://github.com/andrewjiang/HoloClawd-Open-Firmware

## Device Info

- **Model:** HelloCubic-Lite with HoloClawd Firmware
- **Display:** 240x240px ST7789 TFT
- **Default IP:** 192.168.7.80 (configurable)

## Quick Start

**Pomodoro Timer** (Andrew's local version with Spotify integration):

```bash
# Run pomodoro timer with lobster mascot (25 min work, 5 min break)
# Uses hardcoded Spotify URIs for focus/break music
cd ~/Bao/clawd && uv run --script pomodoro.py

# With custom task label (max 20 chars)
cd ~/Bao/clawd && uv run --script pomodoro.py --task "BUILD NETWORK"

# Custom timings
cd ~/Bao/clawd && uv run --script pomodoro.py --work 50 --short 10 --long 20

# Disable Spotify
cd ~/Bao/clawd && uv run --script pomodoro.py --no-spotify
```

**Drawing API** (requires holocube_client.py from repo):

```bash
# Draw something on the display
python3 -c "
from holocube_client import HoloCube, Color, draw_lobster
cube = HoloCube('192.168.7.80')
cube.clear(Color.BLACK)
draw_lobster(cube, 120, 120)  # Draw lobster in center
"
```

## Python Client Library

The `holocube_client.py` module provides full programmatic control:

```python
from holocube_client import HoloCube, Color, draw_lobster, draw_confetti

cube = HoloCube("192.168.7.80")

# Drawing primitives
cube.clear("#000000")                              # Clear screen
cube.pixel(x, y, color)                            # Single pixel
cube.line(x0, y0, x1, y1, color)                   # Line
cube.rect(x, y, w, h, color, fill=True)            # Rectangle
cube.circle(x, y, r, color, fill=True)             # Circle
cube.triangle(x0, y0, x1, y1, x2, y2, color)       # Triangle
cube.ellipse(x, y, rx, ry, color, fill=True)       # Ellipse
cube.roundrect(x, y, w, h, r, color, fill=True)    # Rounded rectangle
cube.text(x, y, "Hello", size=3, color="#00ffff")  # Text

# High-level helpers
cube.centered_text(y, "Centered", size=2)
cube.show_message(["Line 1", "Line 2"], colors=[Color.CYAN, Color.WHITE])
cube.show_timer(seconds, label="FOCUS")
cube.show_progress(0.75, label="Loading")

# Lobster mascot
draw_lobster(cube, 120, 120)                       # Normal lobster
draw_lobster(cube, 120, 120, happy=True, frame=0)  # Party mode with confetti
draw_confetti(cube, 120, 120, frame=1)             # Animate confetti
```

## Pomodoro Timer

Full pomodoro timer with cute lobster buddy. **Use Andrew's local version** at `~/Bao/clawd/pomodoro.py`:

```bash
# Always run from local directory
cd ~/Bao/clawd

# Default: 25 min work, 5 min break (with Spotify)
uv run --script pomodoro.py

# With custom task label
uv run --script pomodoro.py --task "CODE REVIEW"
uv run --script pomodoro.py -t "BUILD NETWORK"

# Custom timings
uv run --script pomodoro.py --work 50 --short 10 --long 20

# Disable Spotify
uv run --script pomodoro.py --no-spotify
```

**Andrew's Version** (~/Bao/clawd/pomodoro.py):
- Hardcoded Spotify URIs:
  - Focus: `spotify:episode:5yJKH11UlF3sS3gcKKaUYx`
  - Break: `spotify:episode:4U4OloHPFBNHWt0GOKENVF`
- Uses `~/clawd/skills/spotify-applescript/spotify.sh` for playback

Options:
- `--task`, `-t`: Task label displayed during work (max 20 chars, auto-uppercased)
- `--work`: Work duration in minutes (default: 25)
- `--short`: Short break in minutes (default: 5)
- `--long`: Long break in minutes (default: 15)
- `--sessions`: Sessions before long break (default: 4)
- `--no-spotify`: Disable automatic music playback

Features:
- Lobster mascot watches you work (focused expression)
- During breaks: happy lobster with twinkling confetti
- Flashing alerts between sessions
- Tracks completed sessions
- Automatic Spotify playback via AppleScript (macOS)
- Water tracker in top-left corner (shared with water.py)

## Water Tracking

Track daily water consumption with a cute water drop icon in the top-left corner:

```bash
cd ~/Bao/clawd

# Show current count
uv run --script water.py

# Add a glass (+1)
uv run --script water.py add

# Add multiple glasses
uv run --script water.py add 2

# Set to specific count
uv run --script water.py set 5

# Reset to 0
uv run --script water.py reset

# Change daily goal
uv run --script water.py goal 10
```

State persists to `~/.holocube_water.json` and auto-resets each day. The water tracker appears in the top-left corner during pomodoro sessions too.

## Stock Firmware Tools

### holocube.py - GIF Upload (Stock Firmware)

```bash
uv run --script holocube.py upload animation.gif
uv run --script holocube.py show animation.gif
uv run --script holocube.py list
```

### gifgen.py - Procedural Animation Generator

```bash
uv run --script gifgen.py fire output.gif
uv run --script gifgen.py plasma output.gif
uv run --script gifgen.py matrix output.gif
uv run --script gifgen.py sparkle output.gif
```

## Drawing API Endpoints

HoloClawd firmware exposes these REST endpoints:

```bash
# Clear screen
curl -X POST http://192.168.7.80/api/v1/draw/clear -d '{"color":"#000000"}'

# Draw shapes
curl -X POST http://192.168.7.80/api/v1/draw/circle -d '{"x":120,"y":120,"r":50,"color":"#ff0000","fill":true}'
curl -X POST http://192.168.7.80/api/v1/draw/rect -d '{"x":10,"y":10,"w":100,"h":50,"color":"#00ff00"}'
curl -X POST http://192.168.7.80/api/v1/draw/triangle -d '{"x0":120,"y0":50,"x1":80,"y1":150,"x2":160,"y2":150,"color":"#0000ff"}'
curl -X POST http://192.168.7.80/api/v1/draw/ellipse -d '{"x":120,"y":120,"rx":60,"ry":30,"color":"#ffff00"}'
curl -X POST http://192.168.7.80/api/v1/draw/line -d '{"x0":0,"y0":0,"x1":240,"y1":240,"color":"#ffffff"}'
curl -X POST http://192.168.7.80/api/v1/draw/text -d '{"x":60,"y":100,"text":"Hello","size":3,"color":"#00ffff"}'

# Batch multiple commands
curl -X POST http://192.168.7.80/api/v1/draw/batch -d '{"commands":[...]}'
```

## Firmware

**Source:** https://github.com/andrewjiang/HoloClawd-Open-Firmware

Build and flash:
```bash
git clone https://github.com/andrewjiang/HoloClawd-Open-Firmware.git
cd HoloClawd-Open-Firmware
pio run                    # Build
curl -X POST -F "file=@.pio/build/esp12e/firmware.bin" http://192.168.7.80/api/v1/ota/fw
```

## Color Reference

```python
Color.BLACK   = "#000000"
Color.WHITE   = "#ffffff"
Color.RED     = "#ff0000"
Color.GREEN   = "#00ff00"
Color.BLUE    = "#0000ff"
Color.CYAN    = "#00ffff"
Color.MAGENTA = "#ff00ff"
Color.YELLOW  = "#ffff00"
Color.ORANGE  = "#ff6600"
Color.PURPLE  = "#9900ff"
```

## Troubleshooting

- **Can't connect**: Check WiFi, device should be at 192.168.7.80
- **Drawing slow**: Each HTTP call takes ~50ms, use batch API for complex drawings
- **Screen flickers**: Only clear screen on first frame, use background colors for text updates
