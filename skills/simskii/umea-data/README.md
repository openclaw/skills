# Umeå Data Skill

Query open data from Umeå kommun about locations, facilities, demographics, environment, and more.

## Installation

```bash
clawdhub install umea-data
```

## Quick Start

### Query a dataset
```bash
./scripts/query.sh badplatser 10
./scripts/query.sh laddplatser 20
```

### Find nearest locations
```bash
# Find nearest EV charging stations to city center
./scripts/nearby.sh laddplatser 63.8258 20.2630 5

# Find nearest playgrounds to Mariehem
./scripts/nearby.sh gop_lekparker 63.8200 20.3000 5
```

## Available Datasets

### Recreation & Facilities
- **gop_lekparker** - Playgrounds managed by Gator och Parker
- **badplatser** - Public swimming spots
- **vandringsleder** - Hiking trails with routes and distances
- **rastplatser** - Rest areas and picnic spots
- **trad-som-forvaltas-av-gator-och-parker** - Trees managed by municipality

### Infrastructure
- **laddplatser** - Electric vehicle charging stations
- **wifi-hotspots** - Public WiFi access points

### Building & Planning
- **bygglov-beslut** - Building permit decisions
- **bygglov-inkomna-arenden** - Building permit applications

### Demographics & Statistics
- **befolkningsfoeraendringar-helar** - Population change statistics
- **bostadsbestand-hustyp** - Housing inventory by type

### Environment
- **vaxthusgasutslapp_umea** - Greenhouse gas emissions data
- **exempel-brottsstatistik-anmaelda-brott-fran-bra-s-oeppna-data** - Crime statistics from BRÅ

## Common Coordinates

- **City center**: 63.8258, 20.2630
- **Mariehem**: 63.8200, 20.3000
- **Universum/Campus**: 63.8190, 20.3070
- **Teg**: 63.8400, 20.2300
- **Holmsund**: 63.7100, 20.3700

## API Information

- Base URL: `https://opendata.umea.se/api/v2/`
- No API key required
- All data is public and open
- Maximum 100 records per request
- Coordinates use WGS84 (lat/lon)

## Natural Language Examples

The AI can answer questions like:
- "Var är närmaste lekplats till Mariehem?"
- "Finns det laddplatser nära centrum?"
- "Vilka badplatser finns i Umeå?"
- "Var kan jag vandra?"
- "Vilka bygglov har beviljats nyligen?"
- "Hur har befolkningen förändrats?"
- "Vad är Umeås växthusgasutsläpp?"
- "Var finns gratis wifi?"

## License

This skill queries public open data from Umeå kommun. Data is provided by Umeå kommun under their open data license.
