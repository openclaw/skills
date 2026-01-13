---
name: skanetrafiken
description: Skåne public transport trip planner (Skånetrafiken). Use when asking about bus/train journeys, departures, schedules, or directions in Skåne, Sweden. Searches stops, plans trips with real-time delays, supports "travel now", "depart at", and "arrive by" modes.
license: MIT
compatibility: Requires curl, jq. Works with Claude Code and compatible agents.
metadata:
  author: rezkam
  version: "1.0.0"
  region: sweden
---

# Skånetrafiken Trip Planner

Plan public transport journeys in Skåne, Sweden with real-time departure information.

**Use `trip.sh` for all journey planning - it handles everything in one call.**

## Supported Locations

- **Stations/Stops** - All bus and train stations in Skåne
- **Addresses** - Street addresses in Skåne and Copenhagen
- **GPS Coordinates** - Any location as lat#lon (e.g., "55.605#13.003")
- **Copenhagen** - Cross-border trips to/from Denmark

## Quick Start

```bash
./trip.sh <from> <to> [datetime] [mode]
```

| Argument | Description |
|----------|-------------|
| `from` | Origin - station name, address, or coordinates |
| `to` | Destination - station name, address, or coordinates |
| `datetime` | Optional: "18:30", "tomorrow 09:00", "2026-01-15 09:00" |
| `mode` | Optional: "depart" (default) or "arrive" |

---

## Examples

### Station to Station

```bash
# Travel now
./trip.sh "Malmö C" "Lund C"

# Depart at 18:30
./trip.sh "Malmö Hyllie" "Malmö C" "18:30"

# Arrive by 09:00 tomorrow
./trip.sh "Malmö C" "Lund C" "tomorrow 09:00" arrive
```

### From Address to Station

```bash
# Address in Malmö to station
./trip.sh "Kalendegatan 12C" "Malmö C" "09:00"

# Full address with city
./trip.sh "Kalendegatan 12C, Malmö" "Lund C"
```

### From GPS Coordinates

```bash
# Coordinates (lat#lon) to station
./trip.sh "55.605#13.003" "Malmö C"
```

### Cross-border to Copenhagen

```bash
# Malmö to Copenhagen Central
./trip.sh "Malmö C" "København H" "18:00"

# To Copenhagen address
./trip.sh "Malmö C" "Amalienborg Slotsplads" "10:00"

# From Lund to Copenhagen
./trip.sh "Lund C" "København H" "tomorrow 09:00"
```

---

## DateTime Formats (Swedish time)

| Format | Example | Meaning |
|--------|---------|---------|
| (empty) | | Travel now |
| `HH:MM` | `"18:30"` | Today at 18:30 |
| `tomorrow HH:MM` | `"tomorrow 09:00"` | Tomorrow at 09:00 |
| `YYYY-MM-DD HH:MM` | `"2026-01-15 09:00"` | Specific date |

---

## Understanding Output

### Example Output

```
Planning trip...

Searching for origin: Malmö C
  Found: Malmö C, Skåne

Searching for destination: Lund C
  Found: Lund C, Skåne

═══════════════════════════════════════════════════════════════
TRIP: Malmö C, Skåne → Lund C, Skåne
TIME: tomorrow 09:00 (depart)
═══════════════════════════════════════════════════════════════

Found 11 journey option(s):

══════════════════════════════════════════════════════════════
OPTION 1: Malmö C → Lund C
══════════════════════════════════════════════════════════════
Date:    2026-01-14
Depart:  09:04
Arrive:  09:16
Changes: 0

LEGS:
  → ORESUND Öresundståg 1324
    From: 09:04 Malmö C [Spår: Se skylt]
    To:   09:16 Lund C [Spår: Se skylt]
    Direction: mot Helsingborg C
```

### Transport Types

| Type | Description |
|------|-------------|
| TRAIN | Pågatåg (regional train) |
| ORESUND | Öresundståg (cross-border train) |
| BUS | Local or regional bus |
| TRAM | Tram/spårvagn |
| WALK | Walking segment |

### Status Indicators

| Status | Meaning |
|--------|---------|
| (no indicator) | On time |
| `[+X min late]` | Delayed X minutes |
| `[-X min early]` | Running early |
| `[PASSED]` | Already departed |
| `⚠️ AVVIKELSE` | Service disruption |

---

## Error Handling

The script provides actionable error messages:

### Location Not Found

```
ERROR: No locations found for origin: 'Malmo'
SUGGESTIONS:
  - Check spelling (Swedish characters: å, ä, ö)
  - Try a more specific name (e.g., 'Malmö C' instead of 'Malmö')
  - For addresses, include city (e.g., 'Kalendegatan 12C, Malmö')
  - For Copenhagen, try 'Köpenhamn' or specific station name
```
**Action**: Retry with corrected spelling or more specific name.

### Multiple Matches

```
NOTE: Found 18 matches for 'Malmö'. Using best match: Malmö C (STOP_AREA)
OTHER OPTIONS:
  - Malmö Hyllie (STOP_AREA) - Skåne
  - Malmö Triangeln (STOP_AREA) - Skåne
```
**Action**: The best match is used automatically. If wrong, use a more specific name.

### No Routes Found

```
No journeys found.
Tips:
  - Try a different time
  - Check if service runs at this hour
  - Try nearby stops
```
**Action**: Retry with different time or nearby stations.

---

## Tips

1. **Use station names directly** - No need to search first, just use names like "Malmö C", "Lund C"
2. **Swedish characters matter** - Use å, ä, ö for Swedish place names
3. **Be specific** - "Malmö C" works better than "Malmö"
4. **Copenhagen names** - Use Danish spelling "København H" or search "Copenhagen"
5. **Coordinates** - Use lat#lon format directly, e.g., "55.605#13.003"

---

## Advanced: Low-level Scripts

For advanced use cases, individual scripts are also available:

| Script | Purpose |
|--------|---------|
| `search-location.sh <name>` | Search for location IDs |
| `journey.sh <from-id> <type> <to-id> <type> [time] [mode]` | Plan with specific IDs |

These are used internally by `trip.sh` and rarely needed directly.
