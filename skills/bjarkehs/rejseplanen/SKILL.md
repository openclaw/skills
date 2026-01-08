---
name: rejseplanen
description: Query Danish public transport departures, arrivals, and journey planning via Rejseplanen API
metadata: {"clawdbot":{"emoji":"🚂","os":["linux","darwin","win32"],"requires":{"bins":["node"]}}}
---

# Rejseplanen - Danish Public Transport

Query real-time train and bus departures, arrivals, and plan journeys via the Rejseplanen API.

## Commands

### Search for stations

```bash
node {baseDir}/dist/rejseplanen.js search "København"
```

### Departures

```bash
node {baseDir}/dist/rejseplanen.js departures Odense
node {baseDir}/dist/rejseplanen.js departures Odense --trains
node {baseDir}/dist/rejseplanen.js departures Odense --trains --to Aalborg
```

### Arrivals

```bash
node {baseDir}/dist/rejseplanen.js arrivals Aalborg
node {baseDir}/dist/rejseplanen.js arrivals Aalborg --trains --from Odense
```

### Trip planning

```bash
node {baseDir}/dist/rejseplanen.js trip Odense Aalborg
node {baseDir}/dist/rejseplanen.js trip Odense "Aalborg Vestby" --time 07:00
```

### Journey details

Show all stops for a specific train:

```bash
node {baseDir}/dist/rejseplanen.js journey Odense 75
```

## Options

- `--trains` - Show only trains
- `--buses` - Show only buses
- `--to <station>` - Filter departures by destination
- `--from <station>` - Filter arrivals by origin
- `--time HH:MM` - Departures after specified time
- `--output json|text` - Output format (default: text)
- `--json` - Shorthand for `--output json`

## JSON output

For programmatic parsing, use `--json`:

```bash
node {baseDir}/dist/rejseplanen.js departures Odense --json
```

## Tips

- Use `search` to find station IDs, then store frequently used ones for faster lookups
- Station IDs can be used directly instead of names (e.g., `008600512` for Odense)
