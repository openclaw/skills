---
name: my-tesla
description: Control Tesla vehicles from macOS via the Tesla Owner API using teslapy (auth, list cars, status, lock/unlock, climate, charging, location, and extras). Use when you want to check your car state or run safe remote commands. Designed for Parth Maniar (@officialpm) with local-only auth caching, confirmation gates for disruptive actions, and chat-friendly status output.
---

# My Tesla

**Author:** Parth Maniar — [@officialpm](https://github.com/officialpm)

A practical Tesla control skill for Clawdbot built on `teslapy`.

## Setup

### Requirements

- `TESLA_EMAIL` env var set (your Tesla account email)
- Python 3.10+

### First-time authentication

```bash
TESLA_EMAIL="you@email.com" python3 {baseDir}/scripts/tesla.py auth
```

This opens a Tesla login URL. Log in, then paste the callback URL back into the CLI.

- Token cache: `~/.tesla_cache.json` (local only; best-effort chmod `0600`)
- Optional: set `MY_TESLA_DEFAULT_CAR` to a vehicle display name to pick a default car via env var
- Or persist a local default with: `python3 {baseDir}/scripts/tesla.py default-car "Name"` (writes `~/.my_tesla.json`; best-effort chmod `0600`)

## Commands

```bash
# List vehicles
python3 {baseDir}/scripts/tesla.py list
python3 {baseDir}/scripts/tesla.py list --json   # machine-readable, privacy-safe

# Version
python3 {baseDir}/scripts/tesla.py version
python3 {baseDir}/scripts/tesla.py --version

# Pick a car (optional)
# --car accepts: exact name, partial name (substring match), or a 1-based index from `list`
python3 {baseDir}/scripts/tesla.py --car "Model" status
python3 {baseDir}/scripts/tesla.py --car 1 report

# Set a default car (used when --car is not passed)
python3 {baseDir}/scripts/tesla.py default-car "My Model 3"

# One-line summary (best for chat)
python3 {baseDir}/scripts/tesla.py summary
python3 {baseDir}/scripts/tesla.py summary --no-wake   # don't wake a sleeping car

# One-screen report (chat friendly, more detail)
# Includes battery/charging/climate + (when available) TPMS tire pressures.
python3 {baseDir}/scripts/tesla.py report
python3 {baseDir}/scripts/tesla.py report --no-wake

# Detailed status
python3 {baseDir}/scripts/tesla.py status
python3 {baseDir}/scripts/tesla.py status --no-wake
python3 {baseDir}/scripts/tesla.py status --summary   # include one-line summary + detailed output
python3 {baseDir}/scripts/tesla.py --car "My Model 3" status

# JSON output (prints ONLY JSON; good for piping/parsing)
# NOTE: `status --json` outputs *raw* `vehicle_data`, which may include location/drive_state.
# Prefer `report --json` (sanitized) unless you explicitly need the raw payload.
python3 {baseDir}/scripts/tesla.py status --json             # raw vehicle_data (may include location)
python3 {baseDir}/scripts/tesla.py report --json             # sanitized report object (no location; includes scheduled charging + charge port state)
python3 {baseDir}/scripts/tesla.py report --json --raw-json  # raw vehicle_data (may include location)
python3 {baseDir}/scripts/tesla.py charge status --json

# Lock / unlock
python3 {baseDir}/scripts/tesla.py lock
python3 {baseDir}/scripts/tesla.py unlock

# Climate (status is read-only)
python3 {baseDir}/scripts/tesla.py climate status
python3 {baseDir}/scripts/tesla.py climate status --no-wake
python3 {baseDir}/scripts/tesla.py climate on
python3 {baseDir}/scripts/tesla.py climate off
python3 {baseDir}/scripts/tesla.py climate defrost on
python3 {baseDir}/scripts/tesla.py climate defrost off
python3 {baseDir}/scripts/tesla.py climate temp 72      # default: °F
python3 {baseDir}/scripts/tesla.py climate temp 22 --celsius

# Charging
python3 {baseDir}/scripts/tesla.py charge status
python3 {baseDir}/scripts/tesla.py charge status --no-wake
python3 {baseDir}/scripts/tesla.py charge start --yes
python3 {baseDir}/scripts/tesla.py charge stop  --yes
python3 {baseDir}/scripts/tesla.py charge limit 80 --yes   # 50–100
python3 {baseDir}/scripts/tesla.py charge amps 16 --yes    # 1–48 (conservative guardrail)

# Scheduled charging (set/off are safety gated)
python3 {baseDir}/scripts/tesla.py scheduled-charging status
python3 {baseDir}/scripts/tesla.py scheduled-charging status --no-wake
python3 {baseDir}/scripts/tesla.py scheduled-charging set 23:30 --yes
python3 {baseDir}/scripts/tesla.py scheduled-charging off --yes

# Location (approx by default; use --yes for precise coordinates)
python3 {baseDir}/scripts/tesla.py location
python3 {baseDir}/scripts/tesla.py location --no-wake
python3 {baseDir}/scripts/tesla.py location --yes

# Tire pressures (TPMS)
python3 {baseDir}/scripts/tesla.py tires
python3 {baseDir}/scripts/tesla.py tires --no-wake

# Openings (doors/trunks/windows)
python3 {baseDir}/scripts/tesla.py openings
python3 {baseDir}/scripts/tesla.py openings --no-wake
python3 {baseDir}/scripts/tesla.py openings --json

# Trunk / frunk (safety gated)
python3 {baseDir}/scripts/tesla.py trunk trunk --yes
python3 {baseDir}/scripts/tesla.py trunk frunk --yes

# Windows (safety gated)
python3 {baseDir}/scripts/tesla.py windows vent  --yes
python3 {baseDir}/scripts/tesla.py windows close --yes

# Sentry Mode (status is read-only; on/off safety gated)
python3 {baseDir}/scripts/tesla.py sentry status
python3 {baseDir}/scripts/tesla.py sentry status --no-wake
python3 {baseDir}/scripts/tesla.py sentry on  --yes
python3 {baseDir}/scripts/tesla.py sentry off --yes

# Charge port door
python3 {baseDir}/scripts/tesla.py charge-port status
python3 {baseDir}/scripts/tesla.py charge-port status --no-wake
python3 {baseDir}/scripts/tesla.py charge-port status --json

# Mileage tracking (odometer) — local SQLite
python3 {baseDir}/scripts/tesla.py mileage init
python3 {baseDir}/scripts/tesla.py mileage record --no-wake --auto-wake-after-hours 24
python3 {baseDir}/scripts/tesla.py mileage status
python3 {baseDir}/scripts/tesla.py mileage export --format csv
python3 {baseDir}/scripts/tesla.py mileage export --format json

# Charge port door open/close (safety gated)
python3 {baseDir}/scripts/tesla.py charge-port open  --yes
python3 {baseDir}/scripts/tesla.py charge-port close --yes

# Fun / attention-grabbing
python3 {baseDir}/scripts/tesla.py honk   --yes
python3 {baseDir}/scripts/tesla.py flash  --yes
```

## Safety defaults

Some actions require an explicit confirmation flag:
- `unlock`, `charge start|stop|limit|amps`, `trunk`, `windows`, `sentry on|off`, `honk`, `flash`, `charge-port open|close`, and `scheduled-charging set|off` require `--yes`
- `location` is *approximate* by default; add `--yes` for precise coordinates

## Privacy

- Credentials are cached locally only (`~/.tesla_cache.json`).
- Do not commit tokens, logs, VINs, or location outputs.
