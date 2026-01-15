# Swisstopo API Referenz

Vollständige Doku: https://api3.geo.admin.ch/

## Koordinatensysteme

| Code | Name | Beschreibung |
|------|------|--------------|
| 4326 | WGS84 | GPS-Koordinaten (lat/lon) |
| 2056 | LV95 | Schweizer Landeskoordinaten (E/N) |
| 21781 | LV03 | Altes CH-System (y/x) |

### Umrechnung WGS84 ↔ LV95

**Grobe Näherung (±100m Genauigkeit):**
```
E = 2600000 + (lon - 7.4) * 73000
N = 1200000 + (lat - 46.95) * 111000
```

**Offizielle Transformation:**
```bash
curl -s "https://geodesy.geo.admin.ch/reframe/wgs84tolv95?easting=LON&northing=LAT"
```

## API Endpoints

### SearchServer
```
GET https://api3.geo.admin.ch/rest/services/api/SearchServer
```

| Parameter | Beschreibung |
|-----------|--------------|
| searchText | Suchbegriff (URL-encoded) |
| type | `locations`, `layers`, `featuresearch` |
| sr | Koordinatensystem (4326, 2056, 21781) |
| bbox | Bounding Box für räumliche Einschränkung |
| limit | Max. Anzahl Ergebnisse |
| origins | Filter: address, parcel, sn25, gg25, district, canton, gazetteer, zipcode |

**Response-Felder:**
- `attrs.label` — Anzeigename
- `attrs.lat`, `attrs.lon` — Koordinaten
- `attrs.origin` — Typ (address, gazetteer, etc.)
- `attrs.detail` — Zusatzinfo (PLZ, Gemeinde, Kanton)

### Height Service
```
GET https://api3.geo.admin.ch/rest/services/height
```

| Parameter | Beschreibung |
|-----------|--------------|
| easting | E-Koordinate |
| northing | N-Koordinate |
| sr | Koordinatensystem (nur 2056 oder 21781!) |

**Response:**
```json
{"height": "1234.5"}
```

### Profile Service
```
GET https://api3.geo.admin.ch/rest/services/profile.json
```

| Parameter | Beschreibung |
|-----------|--------------|
| geom | LineString als JSON |
| sr | Koordinatensystem |
| nb_points | Anzahl Punkte im Profil |
| offset | Startpunkt-Offset |

**Beispiel:**
```bash
curl -s "https://api3.geo.admin.ch/rest/services/profile.json?geom={\"type\":\"LineString\",\"coordinates\":[[7.4,46.9],[7.5,47.0]]}&sr=4326&nb_points=100"
```

### Identify Service
```
GET https://api3.geo.admin.ch/rest/services/api/MapServer/identify
```

| Parameter | Beschreibung |
|-----------|--------------|
| geometry | Punkt: `lon,lat` |
| geometryType | `esriGeometryPoint` |
| layers | `all:layer_id` oder `all:layer1,layer2` |
| sr | Koordinatensystem |
| tolerance | Toleranz in Pixeln |
| imageDisplay | Bildgrösse (z.B. `500,500,96`) |
| mapExtent | Kartenausdehnung |

### Layer Metadata
```
GET https://api3.geo.admin.ch/rest/services/api/MapServer
GET https://api3.geo.admin.ch/rest/services/api/MapServer/LAYER_ID
```

## Wichtige Layer-IDs

### Grenzen
- `ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill` — Gemeinden
- `ch.swisstopo.swissboundaries3d-bezirk-flaeche.fill` — Bezirke
- `ch.swisstopo.swissboundaries3d-kanton-flaeche.fill` — Kantone
- `ch.swisstopo.swissboundaries3d-land-flaeche.fill` — Landesgrenze

### Topografie
- `ch.swisstopo.swisstlm3d-wanderwege` — Wanderwege
- `ch.swisstopo.vec25-gwn-wassernetz` — Gewässernetz
- `ch.swisstopo-karto.hangneigung` — Hangneigung

### Naturschutz
- `ch.bafu.bundesinventare-flachmoore` — Flachmoore
- `ch.bafu.bundesinventare-hochmoore` — Hochmoore
- `ch.bafu.schutzgebiete-paerke_nationaler_bedeutung` — Pärke
- `ch.bafu.bundesinventare-amphibien` — Amphibienlaichgebiete

### Gefahren
- `ch.bafu.gefahren-lawinen` — Lawinengefahren
- `ch.bafu.gefahren-hochwasser` — Hochwasser
- `ch.bafu.gefahren-sturz` — Sturzgefahren

### Verkehr
- `ch.sbb.geschaeftsstellen` — SBB Geschäftsstellen
- `ch.bav.haltestellen-oev` — ÖV-Haltestellen
- `ch.astra.strassennetzkarte` — Strassennetz

### Winter & Touren
- `ch.swisstopo-karto.skitouren` — Skitouren
- `ch.swisstopo-karto.schneeschuhrouten` — Schneeschuhrouten
- `ch.swisstopo-karto.hangneigung` — Hangneigung
- `ch.swisstopo.unterkuenfte-winter` — Winterunterkünfte/Hütten

### Wetter & Hydrologie
- `ch.meteoschweiz.gefahren-warnungen` — MeteoSwiss Warnungen
- `ch.bafu.hydroweb-messstationen_gefahren` — Hochwasser-Messstationen
- `ch.bafu.hydroweb-warnkarte_national` — Hochwasserwarnkarte

## Map Viewer URL-Parameter

Basis: `https://map.geo.admin.ch/`

| Parameter | Beschreibung |
|-----------|--------------|
| lang | de, fr, it, rm, en |
| topic | ech (Standard), geol, luftbild, etc. |
| bgLayer | Hintergrundlayer |
| E, N | Zentrum (WGS84 oder LV95) |
| zoom | 0-13 |
| layers | Aktive Layer (kommagetrennt) |
| layers_opacity | Deckkraft (0-1) |
| layers_visibility | true/false |

**Hintergrund-Layer:**
- `ch.swisstopo.pixelkarte-farbe` — Landeskarte farbig
- `ch.swisstopo.pixelkarte-grau` — Landeskarte grau
- `ch.swisstopo.swissimage` — Luftbild
- `void` — Kein Hintergrund

**Beispiel mit Layern:**
```
https://map.geo.admin.ch/?lang=de&E=7.45&N=46.95&zoom=10&layers=ch.swisstopo.swisstlm3d-wanderwege&bgLayer=ch.swisstopo.pixelkarte-farbe
```

## Weitere Schweizer Datenquellen

### Wetter & Naturgefahren
- **MeteoSwiss Open Data**: https://www.meteoswiss.admin.ch/services-and-publications/service/open-data.html
- **SLF Lawinenbulletin**: https://www.slf.ch/de/lawinenbulletin-und-schneesituation.html
- **BAFU Hydrodaten**: https://www.hydrodaten.admin.ch/de/aktuelle-lage

### Mobilität
- **SBB Open Data**: https://data.sbb.ch/
- **opentransportdata.swiss**: https://opentransportdata.swiss/

### Allgemein
- **opendata.swiss**: https://opendata.swiss/ — Zentraler OGD-Katalog der Schweiz
- **LINDAS**: https://lindas.admin.ch/ — Linked Data Service des Bundes
- **Awesome OGD Switzerland**: https://github.com/rnckp/awesome-ogd-switzerland
