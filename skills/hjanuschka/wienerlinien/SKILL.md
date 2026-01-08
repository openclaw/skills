---
name: wienerlinien
description: Vienna public transport (Wiener Linien) real-time data. Use when asking about departures, schedules, disruptions, elevator status, or directions in Vienna's public transport (U-Bahn, tram, bus, night bus). Queries stops, lines, and traffic info.
---

# Wiener Linien Real-Time API

Query Vienna's public transport for real-time departures, disruptions, elevator outages, and service information.

## Quick Reference

| Endpoint | Purpose |
|----------|---------|
| `/monitor` | Real-time departures at a stop |
| `/trafficInfoList` | All current disruptions |
| `/trafficInfo` | Specific disruption details |
| `/newsList` | Service news & elevator maintenance |

**Base URL:** `https://www.wienerlinien.at/ogd_realtime`

---

## Finding Stop IDs

Stops are identified by **RBL numbers** (Rechnergestütztes Betriebsleitsystem). Use the reference data:

```bash
# Search stops by name
curl -s "https://www.wienerlinien.at/ogd_realtime/doku/ogd/wienerlinien-ogd-haltepunkte.csv" | grep -i "stephansplatz"

# Format: StopID;DIVA;StopText;Municipality;MunicipalityID;Longitude;Latitude
```

**Common Stop IDs (RBL):**

| Stop | RBL IDs | Lines |
|------|---------|-------|
| Stephansplatz | 252, 4116, 4119 | U1, U3 |
| Karlsplatz | 143, 144, 4101, 4102 | U1, U2, U4 |
| Westbahnhof | 1346, 1350, 1368 | U3, U6 |
| Praterstern | 4205, 4210 | U1, U2 |
| Schwedenplatz | 1489, 1490, 4103 | U1, U4 |
| Schottentor | 40, 41, 4118 | U2, Trams |

---

## 1. Real-Time Departures (`/monitor`)

Get next departures at one or more stops.

### Request

```bash
# Single stop
curl -s "https://www.wienerlinien.at/ogd_realtime/monitor?stopId=252"

# Multiple stops
curl -s "https://www.wienerlinien.at/ogd_realtime/monitor?stopId=252&stopId=4116"

# With disruption info
curl -s "https://www.wienerlinien.at/ogd_realtime/monitor?stopId=252&activateTrafficInfo=stoerungkurz&activateTrafficInfo=stoerunglang&activateTrafficInfo=aufzugsinfo"
```

### Parameters

| Param | Required | Description |
|-------|----------|-------------|
| `stopId` | Yes (1-n) | RBL stop ID(s) |
| `activateTrafficInfo` | No | Include disruptions: `stoerungkurz`, `stoerunglang`, `aufzugsinfo` |
| `aArea` | No | `1` = include all platforms with same DIVA number |

### Response Structure

```json
{
  "data": {
    "monitors": [{
      "locationStop": {
        "properties": {
          "name": "60201234",      // DIVA number
          "title": "Stephansplatz", // Stop name
          "attributes": { "rbl": 252 }
        },
        "geometry": {
          "coordinates": [16.3726, 48.2085]  // lon, lat (WGS84)
        }
      },
      "lines": [{
        "name": "U1",
        "towards": "Leopoldau",
        "direction": "H",           // H=hin, R=retour
        "type": "ptMetro",
        "barrierFree": true,
        "realtimeSupported": true,
        "trafficjam": false,
        "departures": {
          "departure": [{
            "departureTime": {
              "timePlanned": "2025-01-08T19:30:00.000+0100",
              "timeReal": "2025-01-08T19:31:30.000+0100",
              "countdown": 3  // minutes until departure
            }
          }]
        }
      }]
    }]
  },
  "message": { "value": "OK", "messageCode": 1 }
}
```

### Key Fields

| Field | Description |
|-------|-------------|
| `countdown` | Minutes until departure |
| `timePlanned` | Scheduled departure |
| `timeReal` | Real-time prediction (if available) |
| `barrierFree` | Wheelchair accessible |
| `trafficjam` | Traffic jam affecting arrival |
| `type` | `ptMetro`, `ptTram`, `ptBusCity`, `ptBusNight` |

---

## 2. Disruptions (`/trafficInfoList`)

Get all current service disruptions.

### Request

```bash
# All disruptions
curl -s "https://www.wienerlinien.at/ogd_realtime/trafficInfoList"

# Filter by line
curl -s "https://www.wienerlinien.at/ogd_realtime/trafficInfoList?relatedLine=U3&relatedLine=U6"

# Filter by stop
curl -s "https://www.wienerlinien.at/ogd_realtime/trafficInfoList?relatedStop=252"

# Filter by type
curl -s "https://www.wienerlinien.at/ogd_realtime/trafficInfoList?name=aufzugsinfo"
```

### Parameters

| Param | Description |
|-------|-------------|
| `relatedLine` | Line name (U1, 13A, etc.) - can repeat |
| `relatedStop` | RBL stop ID - can repeat |
| `name` | Category: `stoerunglang`, `stoerungkurz`, `aufzugsinfo`, `fahrtreppeninfo` |

### Response

```json
{
  "data": {
    "trafficInfos": [{
      "name": "eD_23",
      "title": "Gumpendorfer Straße",
      "description": "U6 Bahnsteig Ri. Siebenhirten - Aufzug außer Betrieb",
      "priority": "1",
      "time": {
        "start": "2025-01-08T06:00:00.000+0100",
        "end": "2025-01-08T22:00:00.000+0100"
      },
      "relatedLines": ["U6"],
      "relatedStops": [4611],
      "attributes": {
        "status": "außer Betrieb",
        "station": "Gumpendorfer Straße",
        "location": "U6 Bahnsteig Ri. Siebenhirten"
      }
    }],
    "trafficInfoCategories": [{
      "id": 1,
      "name": "aufzugsinfo",
      "title": "Aufzugsstörungen"
    }]
  }
}
```

### Disruption Categories

| Name | Description |
|------|-------------|
| `stoerunglang` | Long-term disruptions |
| `stoerungkurz` | Short-term disruptions |
| `aufzugsinfo` | Elevator outages |
| `fahrtreppeninfo` | Escalator outages |

---

## 3. Specific Disruption (`/trafficInfo`)

Get details for a specific disruption by name.

```bash
curl -s "https://www.wienerlinien.at/ogd_realtime/trafficInfo?name=eD_265&name=eD_37"
```

---

## 4. Service News (`/newsList`)

Planned maintenance, elevator service windows, news.

```bash
# All news
curl -s "https://www.wienerlinien.at/ogd_realtime/newsList"

# Filter by line/stop/category
curl -s "https://www.wienerlinien.at/ogd_realtime/newsList?relatedLine=U6&name=aufzugsservice"
```

### Categories

| Name | Description |
|------|-------------|
| `aufzugsservice` | Planned elevator maintenance |
| `news` | General service news |

---

## Reference Data (CSV)

### Stops (Haltepunkte) - Primary

```bash
curl -s "https://www.wienerlinien.at/ogd_realtime/doku/ogd/wienerlinien-ogd-haltepunkte.csv"
# StopID;DIVA;StopText;Municipality;MunicipalityID;Longitude;Latitude
```

**StopID is the RBL number used in API calls.**

### Stations (Haltestellen)

```bash
curl -s "https://www.wienerlinien.at/ogd_realtime/doku/ogd/wienerlinien-ogd-haltestellen.csv"
# DIVA;PlatformText;Municipality;MunicipalityID;Longitude;Latitude
```

### Lines

```bash
curl -s "https://www.wienerlinien.at/ogd_realtime/doku/ogd/wienerlinien-ogd-linien.csv"
# LineID;LineText;SortingHelp;Realtime;MeansOfTransport
```

**MeansOfTransport:** `ptMetro`, `ptTram`, `ptBusCity`, `ptBusNight`

---

## Common Use Cases

### "When is the next U1 from Stephansplatz?"

```bash
# Stephansplatz U1 platform RBL: 4116
curl -s "https://www.wienerlinien.at/ogd_realtime/monitor?stopId=4116" | jq '.data.monitors[].lines[] | select(.name=="U1") | {line: .name, towards: .towards, departures: [.departures.departure[].departureTime.countdown]}'
```

### "Are there any U-Bahn disruptions?"

```bash
curl -s "https://www.wienerlinien.at/ogd_realtime/trafficInfoList?relatedLine=U1&relatedLine=U2&relatedLine=U3&relatedLine=U4&relatedLine=U6" | jq '.data.trafficInfos[] | {title, description, lines: .relatedLines}'
```

### "Which elevators are out of service?"

```bash
curl -s "https://www.wienerlinien.at/ogd_realtime/trafficInfoList?name=aufzugsinfo" | jq '.data.trafficInfos[] | {station: .attributes.station, location: .attributes.location, status: .attributes.status}'
```

### "Departures from Karlsplatz with all disruption info"

```bash
curl -s "https://www.wienerlinien.at/ogd_realtime/monitor?stopId=143&stopId=144&stopId=4101&stopId=4102&activateTrafficInfo=stoerungkurz&activateTrafficInfo=stoerunglang&activateTrafficInfo=aufzugsinfo"
```

---

## Error Codes

| Code | Meaning |
|------|---------|
| 311 | Database unavailable |
| 312 | Stop does not exist |
| 316 | Rate limit exceeded |
| 320 | Invalid query parameter |
| 321 | Missing required parameter |
| 322 | No data in database |

---

## Vehicle Types

| Type | Description |
|------|-------------|
| `ptMetro` | U-Bahn |
| `ptTram` | Straßenbahn |
| `ptBusCity` | City bus |
| `ptBusNight` | Night bus (N lines) |

---

## Tips

1. **Multiple platforms**: A single station may have multiple RBL IDs (one per platform/direction). Query all for complete departures.

2. **Real-time availability**: Check `realtimeSupported` - some lines only have scheduled times.

3. **Countdown vs timeReal**: Use `countdown` for display, `timeReal` for precise timing.

4. **Barrier-free routing**: Filter by `barrierFree: true` for wheelchair users.

5. **Find stop IDs**: Search the CSV files by station name, then use the StopID as `stopId` parameter.
