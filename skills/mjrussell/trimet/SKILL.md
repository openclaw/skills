---
name: trimet
description: Get Portland transit information including arrivals, trip planning, and alerts. Use when user asks about buses, MAX, trains, or transit in Portland.
homepage: https://trimet.org
metadata:
  clawdbot:
    emoji: "🚃"
    requires:
      bins: ["trimet"]
      env: ["TRIMET_APP_ID"]
---

# TriMet CLI

CLI for TriMet Portland transit data. Check arrivals, plan trips, and view alerts.

## Installation

```bash
npm install -g trimet-cli
```

## Setup

1. Get free API key from https://developer.trimet.org/
2. Set environment variable: `export TRIMET_APP_ID="your-key"`

## Commands

### Arrivals

```bash
trimet arrivals <stop-id>              # Real-time arrivals
trimet arrivals 8383 --line 90         # Filter by route
trimet arrivals 8383 --json
```

### Trip Planning

```bash
trimet trip -f <from> -t <to>
trimet trip -f 8383 -t 9969
trimet trip -f "Pioneer Square" -t "PDX Airport"
trimet trip -f 8383 -t 9969 --arrive-by "5:30 PM"
trimet trip -f 8383 -t 9969 --depart-at "2:00 PM"
trimet trip -f 8383 -t 9969 --json
```

### Next Departures

```bash
trimet next -f <from> -t <to>          # Simplified view
trimet next -f 8383 -t 9969 -c 5       # Show 5 options
trimet next -f 8383 -t 9969 --line 90  # Filter by route
```

### Service Alerts

```bash
trimet alerts                          # All alerts
trimet alerts --route 90               # Alerts for route
trimet alerts --json
```

## Common Stop IDs

- Pioneer Courthouse Square: 8383 (westbound), 8384 (eastbound)
- PDX Airport: 10579
- Portland Union Station: 7787
- Beaverton TC: 9969

## Usage Examples

**User: "When's the next MAX?"**
```bash
trimet arrivals 8383
```

**User: "How do I get to the airport?"**
```bash
trimet trip -f "Pioneer Square" -t "PDX Airport"
```

**User: "I need to be downtown by 5pm"**
```bash
trimet trip -f <user-location-stop> -t 8383 --arrive-by "5:00 PM"
```

**User: "Are there any delays on the Blue Line?"**
```bash
trimet alerts --route 100
```

**User: "Next trains to Beaverton"**
```bash
trimet next -f 8383 -t 9969
```

## Route Numbers

- MAX Blue Line: 100
- MAX Red Line: 90
- MAX Yellow Line: 190
- MAX Orange Line: 290
- MAX Green Line: 200

## Notes

- Stop IDs are displayed at TriMet stops and on trimet.org
- Addresses work for trip planning (e.g., "Pioneer Square, Portland")
- Times support natural formats ("5:30 PM", "17:30")
