---
name: places-aggregator
description: Query Google Places Aggregator API for area insights - count places, list place IDs by location (circle/region/polygon), type, rating, price, and operating status.
homepage: https://developers.google.com/maps/documentation/places-aggregate
metadata: {"moltbot":{"emoji":"📊","requires":{"bins":["bun"],"env":["GOOGLE_PLACES_API_KEY"]},"primaryEnv":"GOOGLE_PLACES_API_KEY"}}
---

# Places Aggregator CLI

Query area insights from Google Places Aggregator API. Count places or get place IDs matching location, type, rating, price, and status filters.

## Setup

Set environment variable:
```bash
export GOOGLE_PLACES_API_KEY=your-api-key
```

Or configure in `~/.moltbot/moltbot.json`:
```json
{
  "skills": {
    "entries": {
      "places-aggregator": {
        "env": {
          "GOOGLE_PLACES_API_KEY": "your-api-key"
        }
      }
    }
  }
}
```

## Commands

### count - Count places (INSIGHT_COUNT)
```bash
bun {baseDir}/scripts/cli.ts count --lat 40.7128 --lng -74.006 --radius 1000 --types restaurant
bun {baseDir}/scripts/cli.ts count --place "ChIJOwg_06VPwokRYv534QaPC8g" --types cafe,bar
bun {baseDir}/scripts/cli.ts count --region "ChIJYeZuBI9YwokRjMDs_IEyCwo" --types restaurant
bun {baseDir}/scripts/cli.ts count --polygon ./area.json --types coffee_shop
```

### list - List place IDs (INSIGHT_PLACES)
```bash
bun {baseDir}/scripts/cli.ts list --lat 40.7128 --lng -74.006 --radius 500 --types coffee_shop
bun {baseDir}/scripts/cli.ts list --lat 40.758 --lng -73.9855 --radius 300 --types restaurant --min-rating 4.5
```

Note: Place IDs only returned when count <= 100.

### both - Get count and place IDs in one request
```bash
bun {baseDir}/scripts/cli.ts both --lat 40.75 --lng -73.98 --radius 200 --types coffee_shop
```

## Location Filters (exactly one required)

### Circle by Coordinates
```bash
--lat <number> --lng <number> --radius <meters>
```
Example: `--lat 40.7128 --lng -74.006 --radius 1000`

### Circle by Place ID
```bash
--place <place_id> [--radius <meters>]
```
Example: `--place ChIJOwg_06VPwokRYv534QaPC8g --radius 500`

### Region
```bash
--region <place_id>
```
Example: `--region ChIJYeZuBI9YwokRjMDs_IEyCwo` (Manhattan)

### Custom Polygon
```bash
--polygon <file_or_json>
```
Accepts JSON file path or inline JSON. Formats supported:
- GeoJSON: `[[lng,lat], [lng,lat], ...]`
- Object array: `[{lat: N, lng: N}, ...]`
- API format: `{coordinates: [{latitude: N, longitude: N}, ...]}`

Polygon must be counterclockwise with first and last point identical (closed).

Example file (`area.json`):
```json
[
  [-74.01, 40.71],
  [-74.00, 40.71],
  [-74.00, 40.72],
  [-74.01, 40.72],
  [-74.01, 40.71]
]
```

Example inline:
```bash
--polygon '[[-74.01,40.71],[-74.00,40.71],[-74.00,40.72],[-74.01,40.72],[-74.01,40.71]]'
```

## Type Filters

At least one of `--types` or `--primary-types` required.

```bash
--types <type1,type2,...>           # Types to include
--exclude-types <type1,type2>       # Types to exclude
--primary-types <type1,type2>       # Primary types to include
--exclude-primary-types <t1,t2>     # Primary types to exclude
```

## Operating Status Filter

```bash
--status <status1,status2>
```
Values: `operational` (or `open`), `closed` (or `permanently_closed`), `temporarily_closed` (or `temp_closed`)

## Price Level Filter

```bash
--price <level1,level2,...>
```
Values: `0`-`4` or `free`/`inexpensive`/`moderate`/`expensive`/`very_expensive`

| Level | Name | Symbol |
|-------|------|--------|
| 0 | Free | - |
| 1 | Inexpensive | $ |
| 2 | Moderate | $$ |
| 3 | Expensive | $$$ |
| 4 | Very Expensive | $$$$ |

## Rating Filter

```bash
--min-rating <1.0-5.0>              # Minimum rating
--max-rating <1.0-5.0>              # Maximum rating
```

## Output Options

```bash
--json                              # Raw JSON response
```

## Examples

```bash
# Count coffee shops in 500m radius
bun {baseDir}/scripts/cli.ts count --lat 40.7484 --lng -73.9857 --radius 500 --types coffee_shop

# List highly-rated restaurants
bun {baseDir}/scripts/cli.ts list --lat 40.758 --lng -73.9855 --radius 300 --types restaurant --min-rating 4.5

# Budget-friendly cafes
bun {baseDir}/scripts/cli.ts count --lat 51.5074 --lng -0.1278 --radius 1000 --types cafe --price 0,1,2

# Only operational restaurants
bun {baseDir}/scripts/cli.ts count --lat 40.7 --lng -74.0 --radius 1000 --types restaurant --status operational

# Bars in Manhattan region
bun {baseDir}/scripts/cli.ts count --region ChIJYeZuBI9YwokRjMDs_IEyCwo --types bar

# Custom polygon area
bun {baseDir}/scripts/cli.ts count --polygon ./downtown.json --types restaurant,cafe

# Get both count and IDs
bun {baseDir}/scripts/cli.ts both --lat 40.75 --lng -73.98 --radius 200 --types coffee_shop --json
```

## Common Place Types

```
restaurant, cafe, bar, coffee_shop, bakery, grocery_store, supermarket,
gym, park, museum, hotel, hospital, pharmacy, bank, atm, gas_station,
parking, school, university, library, movie_theater, shopping_mall
```

Full list: https://developers.google.com/maps/documentation/places/web-service/place-types

## Notes

- Place IDs only returned when count <= 100
- Use `goplaces details <place_id>` to get full place details
- Polygon coordinates must form a closed shape (first = last point)
- Polygon vertices must be in counterclockwise order
- Rating values: 1.0 to 5.0
