---
name: grounding-lite
description: Google Maps Grounding Lite MCP for location search, weather, and routes via mcporter.
homepage: https://developers.google.com/maps/ai/grounding-lite
metadata: {"clawdbot":{"emoji":"🗺️","requires":{"bins":["mcporter"],"env":["GOOGLE_MAPS_API_KEY"]},"primaryEnv":"GOOGLE_MAPS_API_KEY","install":[{"id":"node","kind":"node","package":"mcporter","bins":["mcporter"],"label":"Install mcporter (npm)"}]}}
---

# Grounding Lite

Google Maps Grounding Lite MCP provides AI-grounded location data. Experimental (pre-GA), free during preview.

## Setup

1. Enable the API: `gcloud beta services enable mapstools.googleapis.com`
2. Get an API key from [Cloud Console](https://console.cloud.google.com/apis/credentials)
3. Set env: `export GOOGLE_MAPS_API_KEY="YOUR_KEY"`
4. Configure mcporter:
   ```bash
   mcporter config add grounding-lite \
     --url https://mapstools.googleapis.com/mcp \
     --header "X-Goog-Api-Key=$GOOGLE_MAPS_API_KEY" \
     --system
   ```

## Tools

- **search_places**: Find places, businesses, addresses. Returns AI summaries with Google Maps links.
- **lookup_weather**: Current conditions and forecasts (hourly 48h, daily 7 days).
- **compute_routes**: Travel distance and duration (no turn-by-turn directions).

## Commands

```bash
# Search places
mcporter call grounding-lite.search_places textQuery="pizza near Times Square NYC"

# Weather
mcporter call grounding-lite.lookup_weather location='{"address":"San Francisco, CA"}' unitsSystem=IMPERIAL

# Routes
mcporter call grounding-lite.compute_routes origin='{"address":"SF"}' destination='{"address":"LA"}' travelMode=DRIVE

# List tools
mcporter list grounding-lite --schema
```

## Parameters

**search_places**: `textQuery` (required), `locationBias`, `languageCode`, `regionCode`

**lookup_weather**: `location` (required: address/latLng/placeId), `unitsSystem`, `date`, `hour`

**compute_routes**: `origin`, `destination` (required), `travelMode` (DRIVE/WALK)

## Notes

- Rate limits: search_places 100 QPM (1k/day), lookup_weather 300 QPM, compute_routes 300 QPM
- Include Google Maps links in user-facing output (attribution required)
- Only use with models that don't train on input data
