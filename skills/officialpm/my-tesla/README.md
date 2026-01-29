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

# Set default car (used when you don't pass --car)
python3 scripts/tesla.py default-car "PM’s M3 LR"

# One-line summary (best for chat)
python3 scripts/tesla.py summary

# One-screen report (chat friendly, more detail)
python3 scripts/tesla.py report

# Detailed status
python3 scripts/tesla.py status

python3 scripts/tesla.py --car "My Model 3" lock
python3 scripts/tesla.py climate temp 72      # default: °F
python3 scripts/tesla.py climate temp 22 --celsius
python3 scripts/tesla.py charge limit 80

# Trunk / frunk (safety gated)
python3 scripts/tesla.py trunk trunk --yes
python3 scripts/tesla.py trunk frunk --yes

# Windows (safety gated)
python3 scripts/tesla.py windows vent  --yes
python3 scripts/tesla.py windows close --yes

# Location (sensitive)
python3 scripts/tesla.py location --yes
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Privacy / safety

- Never commit tokens, VINs, or location outputs.
- Some commands (location/trunk/windows/honk/flash) require `--yes`.
