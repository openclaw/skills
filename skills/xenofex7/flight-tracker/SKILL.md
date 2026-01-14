---
name: flight-tracker
description: Simple flight tracking using OpenSky Network API. Track flights in real-time by region, callsign, or airport. No API key required. Use for queries like "What flights are over Switzerland?" or "Track flight SWR123" or "Show arrivals at Zurich airport".
homepage: https://openskynetwork.github.io/opensky-api/
---

# Flight Tracker

Track flights in real-time using the free OpenSky Network API.

## Quick Commands

### Flights over a region (bounding box)
```bash
# Switzerland (lat_min, lat_max, lon_min, lon_max)
curl -s "https://opensky-network.org/api/states/all?lamin=45.8&lomin=5.9&lamax=47.8&lomax=10.5" | \
  jq -r '.states[] | "\(.[1]) - \(.[2]) | Alt: \(.[7])m | Speed: \(.[9])m/s | From: \(.[5])"'
```

### Track specific flight by callsign
```bash
curl -s "https://opensky-network.org/api/states/all?icao24=<aircraft-icao>" | jq .
```

### Get flight info
```bash
# Use helper script
python3 scripts/track.py --region switzerland
python3 scripts/track.py --callsign SWR123
python3 scripts/track.py --airport LSZH
```

## Regions

Pre-defined regions in the script:

- **switzerland**: Swiss airspace
- **europe**: European airspace (rough bounds)
- **zurich**: Area around Zurich
- **geneva**: Area around Geneva

## API Endpoints

### All states
```bash
GET https://opensky-network.org/api/states/all
```

Optional parameters:
- `lamin`, `lomin`, `lamax`, `lomax`: Bounding box
- `icao24`: Specific aircraft (hex code)
- `time`: Unix timestamp (0 = now)

### Response Format

Each flight state contains:
```
[0]  icao24      - Aircraft ICAO24 address (hex)
[1]  callsign    - Flight callsign (e.g., "SWR123")
[2]  origin_country - Country name
[5]  origin      - Origin airport (if available)
[7]  baro_altitude - Altitude in meters
[9]  velocity    - Speed in m/s
[10] heading     - Direction in degrees
[11] vertical_rate - Climb/descent rate in m/s
```

## Airport Codes (ICAO)

Common Swiss airports:
- **LSZH** - Zurich
- **LSGG** - Geneva
- **LSZB** - Bern
- **LSZA** - Lugano
- **LFSB** - Basel-Mulhouse (EuroAirport)

## Notes

- Free API with rate limits (anonymous: 400/day)
- Real-time data from ADS-B receivers worldwide
- No API key required for basic usage
- Data updated every 10 seconds
- Create account for higher limits and historical data
