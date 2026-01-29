# My Tesla

Tesla control skill for Clawdbot.

Author: Parth Maniar — [@officialpm](https://github.com/officialpm)

## What’s inside

- `SKILL.md` — the skill instructions
- `scripts/tesla.py` — the CLI implementation (teslapy)
- `VERSION` + `CHANGELOG.md` — versioning for ClawdHub publishing

## Install / auth

Set `TESLA_EMAIL` and run:

```bash
TESLA_EMAIL="you@email.com" python3 scripts/tesla.py auth
```

This uses a browser-based login flow and stores tokens locally in `~/.tesla_cache.json`.

## Usage

```bash
# List vehicles (shows which one is default)
python3 scripts/tesla.py list

# Pick a car (optional)
# --car accepts: exact name, partial name (substring match), or a 1-based index from `list`
python3 scripts/tesla.py --car "Model" report
python3 scripts/tesla.py --car 1 status

# Set default car (used when you don't pass --car)
python3 scripts/tesla.py default-car "My Model 3"

# One-line summary (best for chat)
python3 scripts/tesla.py summary
python3 scripts/tesla.py summary --no-wake   # don't wake a sleeping car

# One-screen report (chat friendly, more detail)
# Includes battery/charging/climate + (when available) TPMS tire pressures.
python3 scripts/tesla.py report
python3 scripts/tesla.py report --no-wake

# Detailed status
python3 scripts/tesla.py status
python3 scripts/tesla.py status --no-wake

python3 scripts/tesla.py --car "My Model 3" lock
python3 scripts/tesla.py climate temp 72      # default: °F
python3 scripts/tesla.py climate temp 22 --celsius
python3 scripts/tesla.py charge limit 80      # 50–100

# Scheduled charging (set/off are safety gated)
python3 scripts/tesla.py scheduled-charging status
python3 scripts/tesla.py scheduled-charging set 23:30 --yes
python3 scripts/tesla.py scheduled-charging off --yes

# Trunk / frunk (safety gated)
python3 scripts/tesla.py trunk trunk --yes
python3 scripts/tesla.py trunk frunk --yes

# Windows (safety gated)
python3 scripts/tesla.py windows vent  --yes
python3 scripts/tesla.py windows close --yes

# Charge port door (safety gated)
python3 scripts/tesla.py charge-port open  --yes
python3 scripts/tesla.py charge-port close --yes

# Sentry Mode (status is read-only; on/off safety gated)
python3 scripts/tesla.py sentry status
python3 scripts/tesla.py sentry status --no-wake
python3 scripts/tesla.py sentry on  --yes
python3 scripts/tesla.py sentry off --yes

# Location (approx by default; use --yes for precise coordinates)
python3 scripts/tesla.py location
python3 scripts/tesla.py location --no-wake
python3 scripts/tesla.py location --yes

# Tire pressures (TPMS)
python3 scripts/tesla.py tires
python3 scripts/tesla.py tires --no-wake
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Privacy / safety

- Never commit tokens, VINs, or location outputs.
- Some commands (unlock/charge start|stop/trunk/windows/sentry on|off/honk/flash/charge-port open|close/scheduled-charging set|off) require `--yes`.
- Read-only commands support `--no-wake` to avoid waking the car (will fail if the vehicle is asleep/offline).
- `location` shows *approximate* coords by default; add `--yes` for precise coordinates.
