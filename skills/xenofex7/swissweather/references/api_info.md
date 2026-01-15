# MeteoSwiss API Reference

Official Swiss weather data from MeteoSwiss (Federal Office of Meteorology and Climatology).

## Data Sources

### 1. Current Weather Measurements (CSV)

**URL**: `https://data.geo.admin.ch/ch.meteoschweiz.messwerte-aktuell/VQHA80.csv`

**Format**: CSV with semicolon (;) delimiter  
**Update frequency**: Every 10 minutes  
**Authentication**: None required (public data)

**Available fields**:
- `tre200s0` - Air temperature 2m (°C)
- `rre150z0` - Precipitation (mm)
- `sre000z0` - Sunshine duration (min)
- `gre000z0` - Global radiation (W/m²)
- `ure200s0` - Relative humidity (%)
- `tde200s0` - Dew point (°C)
- `dkl010z0` - Wind direction (°)
- `fu3010z0` - Wind speed (km/h)
- `fu3010z1` - Gust peak (km/h)
- `prestas0` - Pressure station level (hPa)
- `pp0qffs0` - Pressure sea level QFF (hPa)
- `pp0qnhs0` - Pressure sea level QNH (hPa)

**Notes**: 
- Missing values are marked with `-`
- Station codes are 3-letter abbreviations (e.g., BER, ZRH, RAG)
- Date format: YYYYMMDDHHMM (UTC)

### 2. Weather Forecast API

**URL**: `https://app-prod-ws.meteoswiss-app.ch/v1/plzDetail?plz={postal_code}`

**Format**: JSON  
**Required Header**: `User-Agent: android-31 ch.admin.meteoswiss-2160000`  
**Authentication**: None required

**Parameters**:
- `plz` - Swiss postal code (4-5 digits, zero-padded to 6 digits)

**Response structure**:
```json
{
  "currentWeather": {
    "location": "Location Name",
    "temperature": 10.5,
    "icon": 2
  },
  "forecast": {
    "dayForecast": [
      {
        "date": "2026-01-15",
        "icon": 2,
        "temperatureMax": 12,
        "temperatureMin": 5,
        "precipitation": 0.5
      }
    ]
  }
}
```

**Status**: ⚠️ As of Jan 2026, this API may be unstable or changed. If it fails, use current weather CSV instead or check MeteoSwiss website for updated endpoints.

### 3. Weather Warnings

**URL**: Check MeteoSwiss app API or use Home Assistant integration  
**Format**: JSON with warning levels and types

**Warning levels**:
- 0 - No danger
- 1 - No/minimal hazard
- 2 - Moderate hazard
- 3 - Significant hazard
- 4 - Severe hazard
- 5 - Very severe hazard

**Warning types**:
Wind, Thunderstorms, Rain, Snow, Slippery roads, Frost, Thaw, Heat waves, Avalanches, Earthquakes, Forest fires, Flood, Drought

## Weather Icon Codes

MeteoSwiss uses numeric codes for weather conditions:

**Day conditions (1-50)**:
- 1 = Sunny
- 2-4 = Partly cloudy
- 5, 35 = Cloudy
- 6, 9, 14, 17 = Rainy
- 8, 11, 16, 19, 22 = Snowy
- 7, 10, 15, 18, 21 = Rain/Snow mix
- 12 = Thunderstorm
- 13, 23-25 = Thunderstorm with rain
- 26 = Windy
- 27-28 = Fog

**Night conditions (101-150)**:
- 101 = Clear night
- 102 = Partly cloudy night
- Similar pattern as day codes +100

## Alternative Data Sources

If MeteoSwiss API is unavailable:

1. **Public CSV data**: Always available at data.geo.admin.ch
2. **MeteoSwiss website**: https://www.meteoschweiz.admin.ch
3. **Open-Meteo**: Free weather API with Swiss coverage (https://open-meteo.com)
4. **SRF Meteo**: Swiss public broadcaster weather data

## Popular Station Codes

### Major Cities
- **BER** - Bern (Zollikofen)
- **BAS** - Basel (Binningen)
- **GVE** - Geneva (Cointrin)
- **LUG** - Lugano
- **ZRH** - Zurich Airport

### Zurich Region
- **KLO** - Zurich (Kloten)
- **SMA** - Säntis (mountain)
- **TAE** - Aadorf/Tänikon
- **REH** - Rünenberg (Schafmatt)
- **RAG** - Rapperswil

### Central Switzerland
- **LUZ** - Lucerne
- **ENG** - Engelberg
- **ALT** - Altdorf

### Mountain Stations
- **SMA** - Säntis (2502m)
- **JUN** - Jungfraujoch (3580m)
- **GUE** - Gütsch ob Andermatt (2283m)
- **PIL** - Pilatus (2106m)

### Ticino
- **LUG** - Lugano
- **COM** - Comprovasco
- **LOC** - Locarno-Monti

## Usage Tips

1. **Current weather**: Use CSV endpoint - always reliable
2. **Location matching**: 
   - Find nearest station to postal code
   - Consider altitude differences
   - Avoid mountain stations for valley locations
3. **Caching**: Data updates every 10 minutes, cache responses
4. **Error handling**: Always have fallback to CSV data

## References

- Official MeteoSwiss: https://www.meteoschweiz.admin.ch
- Open Data Platform: https://data.geo.admin.ch
- Station network: https://www.meteoschweiz.admin.ch/home/messsystem.html
