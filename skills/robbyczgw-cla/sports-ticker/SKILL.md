---
name: sports-ticker
description: Live sports alerts with goal scorers, cards, and match updates. Uses FREE ESPN API. Track any football/soccer team from Premier League, Champions League, La Liga, and more.
---

# Sports Ticker

Track your favorite teams with **FREE live alerts** including goal scorers!

## Quick Start

```bash
# Setup
cp config.example.json config.json
python3 scripts/setup.py  # Interactive setup

# Find team IDs
python3 scripts/setup.py find "Barcelona"

# Test
python3 scripts/ticker.py
```

## Config Example

```json
{
  "teams": [
    {
      "name": "Barcelona",
      "emoji": "🔵🔴",
      "espn_id": "83",
      "espn_leagues": ["esp.1", "uefa.champions"]
    }
  ]
}
```

## Commands

```bash
# Ticker for all teams
python3 scripts/ticker.py

# Live monitor (for cron)
python3 scripts/live_monitor.py

# League scoreboard
python3 scripts/ticker.py league uefa.champions

# ESPN direct
python3 scripts/espn.py leagues
python3 scripts/espn.py scoreboard eng.1
```

## Alert Types

- 🏟️ Kick-off
- ⚽ Goals (with scorer name!)
- 🟥 Red cards (with player name)
- ⏸️ Halftime
- 🏁 Full-time (WIN/LOSS/DRAW)

## ESPN API (Free!)

No key needed. Covers 30+ leagues worldwide.
