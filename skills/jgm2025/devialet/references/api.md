# Devialet HTTP API Reference

Official IP Control API available on DOS 2.14+ firmware.

## Base URL

```
http://<speaker-ip>:80/ipcontrol/v1
```

No authentication required. HTTP only (not HTTPS).

## Namespaces

| Namespace | Description |
|-----------|-------------|
| `/devices/{instance}` | Individual device properties |
| `/systems/{instance}` | System properties (stereo pairs) |
| `/groups/{instance}` | Group control (playback, volume) |

**Instance**: Currently only `current` is supported.

## Endpoints

### Device Information

```
GET /devices/current
```
Returns device properties (name, serial, firmware version).

```
GET /systems/current
```
Returns system properties (for stereo pairs).

### Volume Control

```
GET /groups/current/sources/current/soundControl/volume
```
Returns current volume (0-100).

```
POST /systems/current/sources/current/soundControl/volume
Content-Type: application/json

{"volume": 50}
```
Set volume to specific value (0-100).

```
POST /groups/current/sources/current/soundControl/volumeUp
POST /groups/current/sources/current/soundControl/volumeDown
```
Increment/decrement volume by step (default: ~5).

### Playback Control

```
POST /groups/current/sources/current/playback/play
```
Start or resume playback.

```
POST /groups/current/sources/current/playback/pause
```
Pause playback.

```
POST /groups/current/sources/current/playback/mute
POST /groups/current/sources/current/playback/unmute
```
Mute/unmute audio output.

### Source Selection

```
GET /groups/current/sources
```
List all available sources with their IDs and types.

```
GET /groups/current/sources/current
```
Get current source state.

```
POST /groups/current/sources/{sourceId}/playback/play
```
Switch to specific source by its UUID.

**Source types:**
- `airplay` — AirPlay 2
- `spotify` — Spotify Connect
- `opticaljack` — Optical/Line input
- `bluetooth` — Bluetooth (if supported)
- `roon` — Roon Ready
- `upnp` — UPnP/DLNA

### Power Control (DOS 2.16+)

```
POST /devices/{deviceId}/powerOff
```
Turn off device. **Note:** Requires physical button press to turn back on.

## Example: Switch to Optical Input

```bash
# 1. Get list of sources
curl -s "http://192.168.1.50/ipcontrol/v1/groups/current/sources" | jq

# 2. Find opticaljack sourceId from response
# 3. Switch to it
curl -X POST "http://192.168.1.50/ipcontrol/v1/groups/current/sources/UUID-HERE/playback/play"
```

## Discovery

Speakers advertise via mDNS on port 24242.

**UDP Discovery beacon:**
```
Send: DVL.WHO?
Recv: DVL.HERE + serial
```

**mDNS service type:** `_http._tcp`

**Typical hostnames:**
- `PhantomII98dB-XXXXXXXXXXXX.local`
- `PhantomIDarkChrome-XXXXXXXXXXXX.local`
- `PhantomReactor-XXXXXXXXXXXX.local`

## Notes

- No authentication — use only on trusted networks
- Volume defaults to 35 when switching sources (firmware limitation)
- Stereo pairs share group state — command either speaker
- Response format is JSON
- Empty request body `{}` required for POST commands without parameters
