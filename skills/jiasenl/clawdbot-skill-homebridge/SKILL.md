---
name: homebridge
description: "Control smart home devices via Homebridge Config UI X REST API. Use to list, turn on/off, adjust brightness, color, or temperature of HomeKit-compatible accessories. Supports lights, switches, thermostats, fans, and other Homebridge-managed devices."
homepage: https://github.com/homebridge/homebridge-config-ui-x
metadata: { "clawdbot": { "emoji": "🏠" } }
---

# Homebridge Control

Control smart home devices through Homebridge Config UI X's REST API.

## Prerequisites

1. Homebridge with Config UI X installed and running
2. Credentials file at `~/.clawdbot/credentials/homebridge.json`:
   ```json
   {
     "url": "https://homebridge.local:8581",
     "username": "admin",
     "password": "your-password"
   }
   ```

## API Overview

Homebridge Config UI X exposes a REST API. View full documentation at `{HOMEBRIDGE_URL}/swagger`.

## Authentication

All API calls require a Bearer token. Obtain it first:

```bash
# Get auth token
TOKEN=$(curl -s -X POST "${HOMEBRIDGE_URL}/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${HOMEBRIDGE_USERNAME}\",\"password\":\"${HOMEBRIDGE_PASSWORD}\"}" \
  | jq -r '.access_token')
```

## Common Operations

### List All Accessories

```bash
curl -s "${HOMEBRIDGE_URL}/api/accessories" \
  -H "Authorization: Bearer ${TOKEN}" | jq
```

Response includes accessory `uniqueId`, `serviceName`, `type`, and current `values`.

### Get Accessory Layout (Rooms)

```bash
curl -s "${HOMEBRIDGE_URL}/api/accessories/layout" \
  -H "Authorization: Bearer ${TOKEN}" | jq
```

### Control an Accessory

Use PUT to update accessory characteristics:

```bash
# Turn on a light/switch
curl -s -X PUT "${HOMEBRIDGE_URL}/api/accessories/{uniqueId}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"characteristicType": "On", "value": true}'

# Turn off
curl -s -X PUT "${HOMEBRIDGE_URL}/api/accessories/{uniqueId}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"characteristicType": "On", "value": false}'

# Set brightness (0-100)
curl -s -X PUT "${HOMEBRIDGE_URL}/api/accessories/{uniqueId}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"characteristicType": "Brightness", "value": 50}'

# Set color (Hue: 0-360, Saturation: 0-100)
curl -s -X PUT "${HOMEBRIDGE_URL}/api/accessories/{uniqueId}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"characteristicType": "Hue", "value": 240}'

# Set thermostat target temperature
curl -s -X PUT "${HOMEBRIDGE_URL}/api/accessories/{uniqueId}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"characteristicType": "TargetTemperature", "value": 22}'
```

### Common Characteristic Types

| Type                        | Values         | Description                   |
| --------------------------- | -------------- | ----------------------------- |
| `On`                        | `true`/`false` | Power state                   |
| `Brightness`                | `0-100`        | Light brightness %            |
| `Hue`                       | `0-360`        | Color hue in degrees          |
| `Saturation`                | `0-100`        | Color saturation %            |
| `ColorTemperature`          | `140-500`      | Color temp in Mired           |
| `TargetTemperature`         | `10-38`        | Thermostat target °C          |
| `TargetHeatingCoolingState` | `0-3`          | 0=Off, 1=Heat, 2=Cool, 3=Auto |
| `RotationSpeed`             | `0-100`        | Fan speed %                   |
| `Active`                    | `0`/`1`        | Active state (fans, etc.)     |

## Using the Scripts

For convenience, use the provided scripts:

### List Accessories

```bash
scripts/homebridge_api.py list
scripts/homebridge_api.py list --room "Living Room"
scripts/homebridge_api.py list --type Lightbulb
```

### Control Devices

```bash
# Turn on/off
scripts/homebridge_api.py set <uniqueId> On true
scripts/homebridge_api.py set <uniqueId> On false

# Adjust brightness
scripts/homebridge_api.py set <uniqueId> Brightness 75

# Set color
scripts/homebridge_api.py set <uniqueId> Hue 120
scripts/homebridge_api.py set <uniqueId> Saturation 100
```

### Get Accessory Status

```bash
scripts/homebridge_api.py get <uniqueId>
```

## Tips

- Find your accessory's `uniqueId` by listing all accessories first
- The API documentation at `/swagger` shows all available endpoints
- Characteristic names are case-sensitive (use `On` not `on`)
- Some accessories may have multiple services; check the response for service types
- Token expires after some time; re-authenticate if you get 401 errors
