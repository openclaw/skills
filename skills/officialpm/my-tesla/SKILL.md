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

- Token cache: `~/.tesla_cache.json` (local only)

## Commands

```bash
# List vehicles
python3 {baseDir}/scripts/tesla.py list

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
python3 {baseDir}/scripts/tesla.py --car "My Model 3" status

# Lock / unlock
python3 {baseDir}/scripts/tesla.py lock
python3 {baseDir}/scripts/tesla.py unlock

# Climate
python3 {baseDir}/scripts/tesla.py climate on
python3 {baseDir}/scripts/tesla.py climate off
python3 {baseDir}/scripts/tesla.py climate temp 72      # default: °F
python3 {baseDir}/scripts/tesla.py climate temp 22 --celsius

# Charging
python3 {baseDir}/scripts/tesla.py charge status
python3 {baseDir}/scripts/tesla.py charge status --no-wake
python3 {baseDir}/scripts/tesla.py charge start
python3 {baseDir}/scripts/tesla.py charge stop
python3 {baseDir}/scripts/tesla.py charge limit 80   # 50–100

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

# Charge port door (safety gated)
python3 {baseDir}/scripts/tesla.py charge-port open  --yes
python3 {baseDir}/scripts/tesla.py charge-port close --yes

# Fun / attention-grabbing
python3 {baseDir}/scripts/tesla.py honk   --yes
python3 {baseDir}/scripts/tesla.py flash  --yes
```

## Safety defaults

Some actions require an explicit confirmation flag:
- `unlock`, `charge start|stop`, `trunk`, `windows`, `sentry on|off`, `honk`, `flash`, `charge-port open|close`, and `scheduled-charging set|off` require `--yes`
- `location` is *approximate* by default; add `--yes` for precise coordinates

## Privacy

- Credentials are cached locally only (`~/.tesla_cache.json`).
- Do not commit tokens, logs, VINs, or location outputs.
