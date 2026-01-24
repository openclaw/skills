---
name: spots
description: Exhaustive Google Places search using grid-based scanning. Finds ALL places, not just what Google surfaces.
metadata:
  clawdbot:
    emoji: 📍
    private: true
---

# spots

**Find the hidden gems Google doesn't surface.**

Binary: `~/projects/spots/spots` or `go install github.com/foeken/spots@latest`

## Usage

```bash
# Search by location name
spots "Arnhem Centrum" -r 800 -q "breakfast,brunch" --min-rating 4

# Search by coordinates (share location from Telegram)
spots -c 51.9817,5.9093 -r 500 -q "coffee"

# Get reviews for a place
spots reviews "Koffiebar FRENKIE"

# Export to map
spots "Amsterdam De Pijp" -r 600 -o map --out breakfast.html

# Setup help
spots setup
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `-c, --coords` | lat,lng directly | - |
| `-r, --radius` | meters | 500 |
| `-q, --query` | search terms | breakfast,brunch,ontbijt,café,bakkerij |
| `--min-rating` | 1-5 | - |
| `--min-reviews` | count | - |
| `--open-now` | only open | false |
| `-o, --output` | json/csv/map | json |

## Setup

Needs Google API key with Places API + Geocoding API enabled.

```bash
spots setup  # full instructions
export GOOGLE_PLACES_API_KEY="..."
```

Key stored in 1Password: `op://Echo/Google API Key/credential`

## Source

https://github.com/foeken/spots
