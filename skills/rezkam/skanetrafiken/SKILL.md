---
name: skanetrafiken
description: Skåne public transport trip planner (Skånetrafiken). Plans bus/train journeys with real-time delays. Supports stations, addresses, landmarks, and cross-border trips to Copenhagen.
license: MIT
compatibility: Requires curl, jq. Works with Claude Code and compatible agents.
metadata:
  author: rezkam
  version: "1.1.0"
  region: sweden
---

# Skånetrafiken Trip Planner

Plan public transport journeys in Skåne, Sweden with real-time departure information.

## Command

```bash
./trip.sh <from> <to> [datetime] [mode]
```

| Argument | Description |
|----------|-------------|
| `from` | Origin location |
| `to` | Destination location |
| `datetime` | Optional: `"18:30"`, `"tomorrow 09:00"`, `"2026-01-15 09:00"` |
| `mode` | Optional: `"depart"` (default) or `"arrive"` |

---

## CRITICAL: Query Formatting Rules

**The search API is sensitive to how you format location queries. Follow these rules strictly.**

### DO: Landmarks and POIs

Use the landmark name ONLY. Never append city names.

```bash
# CORRECT - landmark name only
./trip.sh "Malmö C" "Emporia"
./trip.sh "Triangeln" "Turning Torso"
./trip.sh "Stortorget" "Malmö C"

# WRONG - adding city breaks POI search
./trip.sh "Malmö C" "Emporia, Malmö"      # Returns wrong location!
./trip.sh "Triangeln, Malmö" "Malmö C"    # Unnecessary, may fail
```

### DO: Street Addresses

Include city name for addresses to improve accuracy.

```bash
# CORRECT - address with city
./trip.sh "Kalendegatan 12, Malmö" "Lund C"
./trip.sh "Malmö C" "Stora Nygatan 25, Malmö"
./trip.sh "Drottninggatan 5, Helsingborg" "Malmö C"

# ACCEPTABLE - address without city (works if unambiguous)
./trip.sh "Kalendegatan 12" "Malmö C"
```

### DO: Train Stations

Use official station names. Add "C" for central stations.

```bash
# CORRECT - official names
./trip.sh "Malmö C" "Lund C"
./trip.sh "Malmö Hyllie" "Helsingborg C"
./trip.sh "Landskrona" "Malmö Triangeln"

# WRONG - incomplete names
./trip.sh "Malmö" "Lund"                  # Ambiguous!
```

### DO: Copenhagen (Cross-border)

Use Danish station names or search-friendly terms.

```bash
# CORRECT
./trip.sh "Malmö C" "København H"
./trip.sh "Malmö C" "Nørreport"
./trip.sh "Lund C" "Copenhagen Airport"

# ALSO WORKS
./trip.sh "Malmö C" "Köpenhamn"
```

### DO: GPS Coordinates

Use `lat#lon` format directly.

```bash
./trip.sh "55.605#13.003" "Malmö C"
./trip.sh "Malmö C" "55.572#12.973"
```

---

## DO vs DON'T Summary

| Location Type | DO | DON'T |
|--------------|-----|-------|
| **Landmarks/POIs** | `"Emporia"` | `"Emporia, Malmö"` |
| **Shopping centers** | `"Triangeln"` | `"Triangeln, Malmö"` |
| **Attractions** | `"Turning Torso"` | `"Turning Torso, Malmö"` |
| **Street addresses** | `"Storgatan 10, Malmö"` | `"Storgatan 10"` (ambiguous) |
| **Central stations** | `"Malmö C"` | `"Malmö"` or `"Malmö Central"` |
| **Other stations** | `"Malmö Hyllie"` | `"Hyllie station"` |

---

## Examples by Use Case

### Travel Now

```bash
./trip.sh "Malmö C" "Lund C"
./trip.sh "Västra Hamnen" "Emporia"
```

### Depart at Specific Time

```bash
./trip.sh "Malmö C" "København H" "18:30"
./trip.sh "Möllevångstorget" "Malmö C" "tomorrow 08:00"
```

### Arrive by Specific Time

```bash
./trip.sh "Lund C" "Malmö C" "09:00" arrive
./trip.sh "Storgatan 15, Malmö" "Emporia" "10:00" arrive
```

### Address to Landmark

```bash
./trip.sh "Regementsgatan 24, Malmö" "Emporia"
./trip.sh "Södra Förstadsgatan 40, Malmö" "Triangeln"
```

---

## DateTime Formats

All times are Swedish local time (CET/CEST).

| Format | Example | Meaning |
|--------|---------|---------|
| _(empty)_ | | Travel now |
| `HH:MM` | `"18:30"` | Today at 18:30 |
| `tomorrow HH:MM` | `"tomorrow 09:00"` | Tomorrow at 09:00 |
| `YYYY-MM-DD HH:MM` | `"2026-01-15 09:00"` | Specific date |

---

## Output Format

### Journey Option

```
══════════════════════════════════════════════════════════════
OPTION 1: Malmö C → Lund C
══════════════════════════════════════════════════════════════
Date:    2026-01-14
Depart:  09:04
Arrive:  09:16
Changes: 0

LEGS:
  → ORESUND Öresundståg 1324
    From: 09:04 Malmö C [Spår 2b]
    To:   09:16 Lund C [Spår 1]
    Direction: mot Helsingborg C
```

### Transport Types

| Type | Description |
|------|-------------|
| `TRAIN` | Pågatåg (regional train) |
| `ORESUND` | Öresundståg (cross-border train) |
| `BUS` | City or regional bus |
| `WALK` | Walking segment |

### Status Indicators

| Indicator | Meaning |
|-----------|---------|
| _(none)_ | On time |
| `[+X min late]` | Delayed |
| `[-X min early]` | Running early |
| `[PASSED]` | Already departed |
| `⚠️ AVVIKELSE` | Service disruption |

---

## Error Handling

### "No locations found"

The search term returned no results.

**Fix**: Check spelling, use Swedish characters (å, ä, ö), try official names.

### "NOTE: Found X matches"

Multiple locations matched. The best match is used automatically.

**Fix**: If wrong location was selected, use a more specific name.

### "No journeys found"

No routes available for this query.

**Fix**: Try different time, check if service operates at that hour.

---

## Technical Notes

- The script converts addresses and POIs to GPS coordinates internally
- Only `STOP_AREA` (stations) and `LOCATION` (coordinates) are sent to the journey API
- Swedish timezone is used for all time parsing and display
