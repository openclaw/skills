# HealthSync CLI Reference

Complete command reference for the `healthsync` CLI tool.

## Commands

### `healthsync discover [--auto-scan]`

Discover HealthSync devices on local network using Bonjour/mDNS.

**Options:**
- `--auto-scan` - Automatically scan QR from clipboard after discovery

**Output:**
```
Searching for HealthSync devices on local network...
Found 1 device(s):

  iPhone-Marcus
    Host: 192.168.1.42
    Port: 8443
```

**Notes:**
- Uses `_healthsync._tcp` Bonjour service type
- Timeout: 5 seconds for discovery, 3 seconds per service resolution
- Requires both devices on same Wi-Fi network

---

### `healthsync scan [--file <path>] [--name <name>] [--debug-pasteboard]`

Scan QR code and pair with iOS device.

**Options:**
- `--file <path>` - Scan QR from image file instead of clipboard
- `--name <name>` - Client name (default: Mac hostname)
- `--debug-pasteboard` - Print pasteboard types/sizes to debug Universal Clipboard issues

**Clipboard scanning priority:**
1. JSON text (Universal Clipboard - most reliable)
2. PNG image data
3. TIFF image data

**QR Payload format:**
```json
{
  "version": "1",
  "host": "192.168.1.42",
  "port": 8443,
  "code": "abc123",
  "expiresAt": "2026-01-07T12:05:00Z",
  "certificateFingerprint": "a1b2c3..."
}
```

**Validations:**
- Version must be "1"
- Host must be local network
- Code must not be expired
- Fingerprint stored for certificate pinning

---

### `healthsync pair --host <host> --port <port> --code <code> --fingerprint <fp> [--name <name>]`

Manual pairing (alternative to QR scanning).

**Options:**
- `--host` - iOS device IP address
- `--port` - Server port (usually 8443)
- `--code` - One-time pairing code
- `--fingerprint` - Certificate SHA256 fingerprint
- `--name` - Client name (default: Mac hostname)
- `--qr <json>` - Full QR payload as JSON string

---

### `healthsync status [--dry-run]`

Check connection status with paired iOS device.

**Options:**
- `--dry-run` - Print request without connecting

**Output:**
```
Status: ok
Device: iPhone-Marcus
Types: steps, heartRate, sleepAnalysis
```

**Response fields:**
- `status` - "ok" or error state
- `deviceName` - iOS device name
- `enabledTypes` - Health data types with permission
- `serverTime` - Server timestamp (for clock sync validation)

---

### `healthsync types [--dry-run]`

List enabled health data types.

**Output:**
```
steps, distanceWalkingRunning, heartRate, sleepAnalysis
```

---

### `healthsync fetch --start <iso> --end <iso> --types <list> [--format csv|json] [--dry-run]`

Fetch health data from iOS device.

**Required options:**
- `--start` - Start date (ISO 8601: `2026-01-01T00:00:00Z`)
- `--end` - End date (ISO 8601: `2026-12-31T23:59:59Z`)
- `--types` - Comma-separated list of types

**Optional:**
- `--format` - Output format: `csv` (default) or `json`
- `--dry-run` - Print request without fetching

**CSV output format:**
```csv
id;type;value;unit;startDate;endDate;sourceName
uuid;steps;1234;count;2026-01-07T08:00:00Z;2026-01-07T09:00:00Z;iPhone
```

**JSON output format:**
```json
{
  "status": "ok",
  "count": 42,
  "samples": [
    {
      "id": "uuid",
      "type": "steps",
      "value": 1234,
      "unit": "count",
      "startDate": "2026-01-07T08:00:00Z",
      "endDate": "2026-01-07T09:00:00Z",
      "sourceName": "iPhone",
      "metadata": null
    }
  ]
}
```

---

### `healthsync version`

Show version information.

**Output:**
```
HealthSyncCLI v1.0.0
Build: 2026-01-07
Platform: macOS (Version 15.3)

Copyright 2026 Marcus Neves
License: Apache-2.0
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error (message printed to stderr) |

## Environment

- Config: `~/.healthsync/config.json` (0600 permissions)
- Token: macOS Keychain (`org.mvneves.healthsync.cli`)
- Logs: stderr (errors only)

## Build from Source

```bash
cd macOS/HealthSyncCLI
swift build
swift test  # 39 tests

# Run
.build/debug/healthsync --help
```
