# Umeå Data - Open Data från Umeå kommun

Query open data from Umeå kommun about locations, facilities, demographics, environment, and more.

## API Base URL
`https://opendata.umea.se/api/v2/`

## Available Data Categories

### 🏞️ Recreation & Facilities

#### **Lekplatser (Playgrounds)**
- Dataset ID: `gop_lekparker`
- Contains playground locations managed by Gator och Parker
- Fields: namn, omrade, coordinates (geo_point_2d), contact info
- Example: "Var är närmaste lekplats till Mariehem?"

#### **Badplatser (Swimming Spots)**
- Dataset ID: `badplatser`
- Public swimming locations in Umeå
- Fields: namn, omrade, typ, coordinates, handik_anp (accessibility)
- Example: "Vilka badplatser finns i Umeå?"

#### **Vandringsleder (Hiking Trails)**
- Dataset ID: `vandringsleder`
- Hiking trails with routes and distances
- Fields: namn, delstracka, kommun, klass, langd (length in meters), geo_shape (trail geometry)
- Example: "Var kan jag vandra i Umeå?"

#### **Rastplatser (Rest Areas)**
- Dataset ID: `rastplatser`
- Rest stops and picnic areas
- Fields: name, location coordinates
- Example: "Var finns rastplatser?"

#### **Träd (Trees)**
- Dataset ID: `trad-som-forvaltas-av-gator-och-parker`
- Trees managed by Gator och Parker
- Fields: tree type, location, management data
- Example: "Vilka träd finns i området?"

### ⚡ Infrastructure

#### **Laddplatser (EV Charging Stations)**
- Dataset ID: `laddplatser`
- Electric vehicle charging stations
- Fields: name, street, house_number, zipcode, city, owned_by, operator, number_charging_points, available_charging_points, position (lon/lat)
- Example: "Finns det laddplatser nära centrum?"

#### **WiFi Hotspots**
- Dataset ID: `wifi-hotspots`
- Public WiFi access points
- Fields: popularnamn (name), koordinat (coordinates)
- Example: "Var finns gratis wifi i Umeå?"

### 🏗️ Building & Planning

#### **Bygglov Beslut (Building Permit Decisions)**
- Dataset ID: `bygglov-beslut`
- Approved building permits
- Fields: arendebeskrivning, arendetyp, beslut, beslutsdatum, registreringsdatum, beslutstyp
- Example: "Vilka bygglov har beviljats nyligen?"

#### **Bygglov Inkomna Ärenden (Building Permit Applications)**
- Dataset ID: `bygglov-inkomna-arenden`
- Incoming building permit applications
- Fields: application details, submission date, status
- Example: "Hur många bygglovsansökningar har kommit in?"

### 📊 Demographics & Statistics

#### **Befolkningsförändringar (Population Changes)**
- Dataset ID: `befolkningsfoeraendringar-helar`
- Population change statistics
- Fields: year, births, deaths, migration, total change
- Example: "Hur har befolkningen förändrats i Umeå?"

#### **Bostadsbestånd (Housing Stock)**
- Dataset ID: `bostadsbestand-hustyp`
- Housing inventory by type
- Fields: house type, count, area
- Example: "Hur ser bostadsbeståndet ut?"

### 🌍 Environment

#### **Växthusgasutsläpp (Greenhouse Gas Emissions)**
- Dataset ID: `vaxthusgasutslapp_umea`
- Greenhouse gas emissions data for Umeå
- Fields: year, sector, emissions (tons CO2 equivalent)
- Example: "Vad är Umeås växthusgasutsläpp?"

#### **Brottsstatistik (Crime Statistics)**
- Dataset ID: `exempel-brottsstatistik-anmaelda-brott-fran-bra-s-oeppna-data`
- Reported crimes from BRÅ open data
- Fields: crime type, count, year
- Example: "Hur ser brottsstatistiken ut?"

## Usage

### Query a Dataset
```bash
./scripts/query.sh <dataset_id> [limit]
```

Example:
```bash
./scripts/query.sh badplatser 10
./scripts/query.sh laddplatser 20
```

### Find Nearest Location
```bash
./scripts/nearby.sh <dataset_id> <lat> <lon> [limit]
```

Example:
```bash
# Find nearest playground to Mariehem (approx coordinates)
./scripts/nearby.sh gop_lekparker 63.8200 20.3000 5

# Find nearest EV charging station to city center
./scripts/nearby.sh laddplatser 63.8258 20.2630 5
```

## API Endpoints

### List All Datasets
```bash
curl "https://opendata.umea.se/api/v2/catalog/datasets"
```

### Get Records from a Dataset
```bash
curl "https://opendata.umea.se/api/v2/catalog/datasets/{dataset_id}/records?limit=20"
```

### Search Datasets
```bash
curl "https://opendata.umea.se/api/v2/catalog/datasets?where=search(default,\"query\")"
```

## Data Format

All records follow this structure:
```json
{
  "total_count": 123,
  "records": [
    {
      "record": {
        "id": "unique-id",
        "timestamp": "2024-01-01T12:00:00Z",
        "fields": {
          "namn": "Location Name",
          "geo_point_2d": {
            "lat": 63.825,
            "lon": 20.263
          },
          ...
        }
      }
    }
  ]
}
```

## Natural Language Query Examples

The AI can answer questions like:

**Recreation:**
- "Var är närmaste lekplats till Mariehem?"
- "Vilka badplatser finns i Umeå?"
- "Var kan jag vandra?"
- "Finns det någon rastplats nära E4?"

**Infrastructure:**
- "Finns det laddplatser nära centrum?"
- "Var finns gratis wifi?"
- "Hur många laddstolpar finns det totalt?"

**Planning:**
- "Vilka bygglov har beviljats nyligen?"
- "Vad byggs i Umeå just nu?"

**Demographics & Environment:**
- "Hur har befolkningen förändrats?"
- "Vad är Umeås växthusgasutsläpp?"
- "Hur många bostäder finns i Umeå?"
- "Hur ser brottsstatistiken ut?"

## Notes

- No API key required
- All data is public and open
- Coordinates use WGS84 (lat/lon)
- Some datasets include geo_shape for trails/routes
- Updated regularly by Umeå kommun
