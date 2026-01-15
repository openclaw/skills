---
name: swissweather
description: Get current weather and forecasts from MeteoSwiss (official Swiss weather service). Use when querying Swiss weather data, local measurements from Swiss weather stations, or Swiss-specific forecasts. Provides real-time measurements (temperature, humidity, wind, precipitation, pressure) from 100+ Swiss stations and multi-day forecasts by postal code. Ideal for Swiss locations - more accurate than generic weather services for Switzerland.
---

# SwissWeather

Get current weather measurements and forecasts from MeteoSwiss, the official Swiss Federal Office of Meteorology and Climatology.

## Why Use This

- **Official Swiss data**: Direct from MeteoSwiss government service
- **Real measurements**: 100+ automated weather stations across Switzerland
- **No API key required**: Free public data
- **Swiss-optimized**: Better coverage and accuracy for Switzerland than generic services
- **Comprehensive**: Temperature, humidity, wind, precipitation, pressure, sunshine, radiation

## Quick Start

### Current Weather by Station

Get real-time measurements from a specific Swiss weather station:

**Option 1: Shell script (no dependencies)**
```bash
scripts/current_weather_curl.sh --station RAG
```

**Option 2: Python script (requires: pip3 install requests)**
```bash
scripts/current_weather.py --station RAG
```

Example output:
```
Station: RAG
Time: 2026-01-15 11:40 UTC
Temperature (°C)........................ 8.6
Rel. humidity (%)...................... 56.3
Wind speed (km/h)...................... 6.8
Precipitation (mm)..................... 0.0
```

Popular stations:
- **RAG** - Rapperswil (Zurich region)
- **BER** - Bern
- **ZRH** - Zurich Airport
- **BAS** - Basel
- **GVE** - Geneva
- **LUG** - Lugano

### List All Stations

```bash
scripts/current_weather_curl.sh --list
# or
scripts/current_weather.py --list
```

Returns 100+ Swiss weather stations with codes and last update time.

### Forecast by Postal Code

Get multi-day weather forecast:

```bash
scripts/forecast.py 8640            # Rapperswil-Jona
scripts/forecast.py 8001 --days 7   # Zurich, 7-day forecast
```

**Note**: The forecast API may occasionally be unstable. If it fails, fall back to current weather measurements.

## Available Data

### Current Weather Measurements

Updated every 10 minutes from automated stations:

- **Temperature** (°C) - Air temperature at 2m height
- **Humidity** (%) - Relative humidity
- **Wind** - Speed (km/h), direction (°), gust peak
- **Precipitation** (mm) - Recent rainfall
- **Pressure** (hPa) - Station level, sea level
- **Sunshine** (min) - Duration of sunshine
- **Radiation** (W/m²) - Global solar radiation
- **Dew point** (°C)

### Weather Forecasts

Multi-day forecasts by Swiss postal code:

- Daily temperature (min/max)
- Weather conditions with icons
- Precipitation amount and probability
- Hourly forecasts (when available)

## Station Selection

Choose the nearest station to your location:

- **Major cities**: BER (Bern), ZRH (Zurich), BAS (Basel), GVE (Geneva), LUG (Lugano)
- **Zurich region**: KLO (Kloten), RAG (Rapperswil), TAE (Tänikon)
- **Central**: LUZ (Lucerne), ALT (Altdorf), ENG (Engelberg)
- **Mountains**: SMA (Säntis), JUN (Jungfraujoch), PIL (Pilatus)

**Tip**: Avoid mountain stations for valley locations due to altitude differences.

See `references/api_info.md` for complete station list and details.

## JSON Output

All scripts support `--json` flag for programmatic use:

```bash
scripts/current_weather.py --station RAG --json
scripts/forecast.py 8640 --json
```

## Advanced Usage

### Multiple Stations

Show all current measurements:

```bash
scripts/current_weather.py --all
```

### Find Nearest Station

1. List all stations: `scripts/current_weather.py --list`
2. Identify closest by name/location
3. Use that station code

### Caching

Data updates every 10 minutes. Cache responses appropriately:

```bash
# Cache current weather for 5-10 minutes
# Cache forecasts for 1-2 hours
```

## API Reference

See `references/api_info.md` for:
- Complete API documentation
- All available data fields
- Weather icon codes
- Warning levels and types
- Alternative data sources
- Technical details

## Dependencies

```bash
pip3 install requests
```

## Data Source

- **Provider**: MeteoSwiss (Federal Office of Meteorology and Climatology)
- **Authority**: Official Swiss government weather service
- **Update**: Every 10 minutes (current weather)
- **Coverage**: 100+ automated stations across Switzerland
- **URL**: https://data.geo.admin.ch / https://www.meteoschweiz.admin.ch

## Troubleshooting

**Forecast API fails**: The MeteoSwiss app API occasionally changes. If `forecast.py` fails, use current weather measurements instead, or check `references/api_info.md` for alternative methods.

**Station not found**: Use `--list` to see available stations. Station codes are 3-letter abbreviations (case-insensitive).

**Missing data**: Some stations don't measure all parameters. Look for `-` or `N/A` in output.

## Related

- **swiss-transport**: Swiss public transport schedules and connections
- **weather**: Generic weather service (wttr.in) - use swissweather for Switzerland
