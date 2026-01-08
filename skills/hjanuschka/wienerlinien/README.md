# Wiener Linien Skill

A skill for querying Vienna's public transport (Wiener Linien) real-time data including departures, disruptions, and elevator status.

## Overview

This skill provides tools to access Wiener Linien's real-time API for:
- **Real-time departures** at any stop
- **Service disruptions** (short-term and long-term)
- **Elevator outages** at U-Bahn stations
- **Stop search** by name to find RBL stop IDs

## Scripts

### `search-stop.sh` - Find Stop IDs

Search for stops by name to get their RBL (stop) IDs needed for departure queries.

```bash
./search-stop.sh stephansplatz
./search-stop.sh kagran
```

### `departures.sh` - Real-Time Departures

Get next departures from one or more stops. Supports multiple stop IDs for stations with multiple platforms.

```bash
./departures.sh 252              # Single stop
./departures.sh 252 4116 4119    # Multiple platforms (Stephansplatz)
```

### `disruptions.sh` - Service Disruptions

Get current disruptions, optionally filtered by line.

```bash
./disruptions.sh                 # All disruptions
./disruptions.sh U1 U3           # Only U1 and U3
./disruptions.sh 27A             # Specific bus line
```

### `elevators.sh` - Elevator Outages

Get elevator outages at stations, optionally filtered by line.

```bash
./elevators.sh                   # All elevator outages
./elevators.sh U6                # U6 stations only
```

## Common Stop IDs (RBL)

| Stop | RBL IDs | Lines |
|------|---------|-------|
| Stephansplatz | 252, 4116, 4119 | U1, U3 |
| Karlsplatz | 143, 144, 4101, 4102 | U1, U2, U4 |
| Westbahnhof | 1346, 1350, 1368 | U3, U6 |
| Praterstern | 4205, 4210 | U1, U2 |
| Schwedenplatz | 1489, 1490, 4103 | U1, U4 |
| Schottentor | 40, 41, 4118 | U2, Trams |

## API Reference

See [SKILL.md](SKILL.md) for complete API documentation including:
- Full endpoint specifications
- Response structures
- Error codes
- Reference data (CSV downloads)

## Requirements

- `curl` - HTTP requests
- `jq` - JSON parsing

## License

Uses Wiener Linien Open Data: https://www.wienerlinien.at/open-data
