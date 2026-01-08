---
name: healthkit-sync
description: iOS HealthKit data sync CLI commands and patterns. Use when working with healthsync CLI, fetching Apple Health data (steps, heart rate, sleep, workouts), pairing iOS devices over local network, or understanding the iOS Health Sync project architecture including mTLS certificate pinning, Keychain storage, and audit logging.
license: Apache-2.0
compatibility: macOS with healthsync CLI installed (~/.healthsync/config.json)
metadata:
  category: development
  platforms: ios,macos
  author: mneves
---

# HealthKit Sync CLI

Securely sync Apple HealthKit data from iPhone to Mac over local network using mTLS.

## When to Use This Skill

- User asks about syncing health data from iPhone
- User mentions `healthsync` CLI commands
- User wants to fetch steps, heart rate, sleep, or workout data
- User needs to pair a Mac with an iOS device
- User asks about the iOS Health Sync project architecture
- User mentions certificate pinning or mTLS patterns

## CLI Quick Reference

### Pairing Flow (First Time)

```bash
# 1. Discover devices on local network
healthsync discover

# 2. On iOS app: tap "Share" to generate QR code, then "Copy"
# 3. Scan QR from clipboard (Universal Clipboard)
healthsync scan

# Alternative: scan from image file
healthsync scan --file ~/Desktop/qr.png
```

### Fetching Health Data

```bash
# Check connection status
healthsync status

# List enabled data types
healthsync types

# Fetch data as CSV (default)
healthsync fetch --start 2026-01-01T00:00:00Z --end 2026-12-31T23:59:59Z --types steps

# Fetch multiple types as JSON
healthsync fetch --start 2026-01-01T00:00:00Z --end 2026-12-31T23:59:59Z \
  --types steps,heartRate,sleepAnalysis --format json | jq

# Pipe to file
healthsync fetch --start 2026-01-01T00:00:00Z --end 2026-12-31T23:59:59Z \
  --types steps > steps.csv
```

### Available Health Data Types

**Activity**: steps, distanceWalkingRunning, distanceCycling, activeEnergyBurned, basalEnergyBurned, exerciseTime, standHours, flightsClimbed, workouts

**Heart**: heartRate, restingHeartRate, walkingHeartRateAverage, heartRateVariability

**Vitals**: bloodPressureSystolic, bloodPressureDiastolic, bloodOxygen, respiratoryRate, bodyTemperature, vo2Max

**Sleep**: sleepAnalysis, sleepInBed, sleepAsleep, sleepAwake, sleepREM, sleepCore, sleepDeep

**Body**: weight, height, bodyMassIndex, bodyFatPercentage, leanBodyMass

## Configuration

Config stored at `~/.healthsync/config.json` (permissions: 0600):
```json
{
  "host": "192.168.1.x",
  "port": 8443,
  "fingerprint": "sha256-certificate-fingerprint"
}
```

Token stored in macOS Keychain under service `org.mvneves.healthsync.cli`.

## Security Architecture

### Certificate Pinning

The CLI validates server certificates by SHA256 fingerprint (TOFU model):
1. First pairing stores fingerprint from QR code
2. Subsequent connections verify fingerprint matches
3. Mismatch = connection rejected (MITM protection)

### Local Network Only

Host validation restricts connections to:
- `localhost`, `*.local` domains
- Private IPv4: `192.168.*`, `10.*`, `172.16-31.*`
- IPv6 loopback: `::1`, link-local: `fe80::`

### Keychain Storage

Tokens never stored in config file - always in Keychain with:
- `kSecAttrAccessibleWhenUnlocked` protection class
- Service: `org.mvneves.healthsync.cli`
- Account: `token-{host}`

## Project Structure

```
ai-health-sync-ios-clawdbot/
├── iOS Health Sync App/          # Swift 6 iOS app
│   ├── Services/Security/        # CertificateService, KeychainStore, PairingService
│   ├── Services/HealthKit/       # HealthKitService, HealthSampleMapper
│   ├── Services/Network/         # NetworkServer (TLS), HTTPTypes
│   └── Services/Audit/           # AuditService (SwiftData)
└── macOS/HealthSyncCLI/          # Swift Package CLI
```

## Troubleshooting

**"No devices found"**:
- Ensure iOS app is running with sharing enabled
- Both devices must be on same Wi-Fi network
- Check firewall isn't blocking mDNS (port 5353)

**"Pairing code expired"**:
- Generate new QR code on iOS app (codes expire in 5 minutes)

**"Certificate mismatch"**:
- Delete `~/.healthsync/config.json` and re-pair
- Server certificate may have been regenerated

**"Connection refused"**:
- iOS app server may not be running
- Run `healthsync status --dry-run` to test without connecting

## See Also

- [CLI Reference](references/CLI-REFERENCE.md) - Detailed command documentation
- [Security Patterns](references/SECURITY.md) - mTLS and certificate pinning patterns
- [Architecture](references/ARCHITECTURE.md) - iOS app architecture details
