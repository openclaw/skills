---
name: weather-pollen
description: Weather and pollen reports for any location using free APIs. Get current conditions, forecasts, and pollen data.
metadata: {"clawdbot":{"emoji":"🌤️","requires":{"bins":["curl"]}}}
---

# Weather and Pollen Skill

Get weather and pollen reports for any location using free APIs.

## Tools

### weather_report
Get weather and pollen data for a specified location.

**Args:**
- `includePollen` (boolean, default: true) - Include pollen data
- `location` (string, optional) - Location name to display (coordinates configured via env)

## Configuration

Set location via environment variables (defaults to Anna, TX):
- `WEATHER_LAT` - Latitude
- `WEATHER_LON` - Longitude
- `WEATHER_LOCATION` - Location display name

## APIs Used
- **Weather:** Open-Meteo (free, no API key)
- **Pollen:** Pollen.com (free, no API key)
