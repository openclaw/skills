---
name: apple-media
description: Discover and control Apple media/AirPlay devices (HomePod, Apple TV, AirPlay speakers) from macOS. Use when you want to scan for AirPlay devices, map names→IPs/IDs, pair/connect, and control playback/volume using pyatv (atvremote) and Airfoil.
---

# Apple Media (AirPlay + Apple TV control)

**Author:** Parth Maniar — [@officialpm](https://github.com/officialpm)

This skill is a thin workflow wrapper around two tools:

- **pyatv** (`atvremote`) for discovering Apple TVs/HomePods and (when supported/paired) remote-control style commands.
- **Airfoil** (via the existing `airfoil` skill) for reliable **speaker connect/disconnect + volume** control across AirPlay speakers (including HomePods).

## Setup

This skill uses `pyatv` installed via **pipx**.

Install/repair (pinned to Python 3.12 to avoid Python 3.14 asyncio issues):

```bash
pipx install pyatv || pipx upgrade pyatv
pipx reinstall pyatv --python python3.12
```

Verify:

```bash
atvremote --help | head
```

## Quick start

### 1) Scan the network for devices

```bash
# Fast scan (5s)
./scripts/scan.sh 5

# Faster scan when you know IP(s)
./scripts/scan-hosts.sh "10.0.0.28,10.0.0.111" 3

# Or JSON output
node ./scripts/scan-json.js 5
```

You’ll see devices like:
- HomePods (e.g., "Living Room", "Bedroom")
- Apple TV
- AirPlay-capable TVs

### 2) Control HomePod / speaker volume (recommended path)

Use Airfoil for speaker control (reliable for HomePods):

```bash
# List speakers Airfoil can see
../airfoil/airfoil.sh list

# Connect and set volume
./scripts/connect.sh "Living Room"
./scripts/volume.sh "Living Room" 35

# Disconnect (direct)
../airfoil/airfoil.sh disconnect "Living Room"
```

### 3) Apple TV remote commands (pyatv)

First, scan to find the Apple TV name or id, then run commands:

```bash
# Examples (device name can be Apple TV or other targets)
atvremote -n "TV" playing
atvremote -n "TV" play_pause
atvremote -n "TV" turn_on
atvremote -n "TV" turn_off
```

If you get auth/protocol errors, pairing/credentials are needed (device-dependent).

## Notes / gotchas

- **pyatv HomePod control often requires authentication** and may not support all remote-control commands out of the box.
  - When pyatv fails for HomePod playback/volume, prefer **Airfoil** for volume + speaker routing.
- `atvremote scan` is the source of truth for IP/ID discovery.

## Bundled scripts

### `scripts/scan.sh`

Runs `atvremote scan` with a configurable timeout.

```bash
./scripts/scan.sh 5
```

### `scripts/scan-json.js`

Parses `atvremote scan` output into a compact JSON summary (name, address, model, services).

```bash
node ./scripts/scan-json.js
```
