---
name: unifi
description: Query and monitor UniFi network via local gateway API (Cloud Gateway Max / UniFi OS). Use when the user asks to "check UniFi", "list UniFi devices", "show who's on the network", "UniFi clients", "UniFi health", "top apps", "network alerts", "UniFi DPI", or mentions UniFi monitoring/status/dashboard.
version: 1.0.0
metadata:
  clawdbot:
    emoji: "📡"
    requires:
      bins: ["curl", "jq"]
---

# UniFi Network Monitoring Skill

Monitor and query your UniFi network via the local UniFi OS gateway API (tested on Cloud Gateway Max).

## Purpose

This skill provides **read-only** access to your UniFi network's operational data:
- Devices (APs, switches, gateway) status and health
- Active clients (who's connected where)
- Network health overview
- Traffic insights (top applications via DPI)
- Recent alarms and events

All operations are **GET-only** and safe for monitoring/reporting.

## Setup

Create the credentials file: `~/.clawdbot/credentials/unifi/config.json`

```json
{
  "url": "https://10.1.0.1",
  "username": "api",
  "password": "YOUR_PASSWORD",
  "site": "default"
}
```

- `url`: Your UniFi OS gateway IP/hostname (HTTPS)
- `username`: Local UniFi OS admin username
- `password`: Local UniFi OS admin password
- `site`: Site name (usually `default`)

## Commands

All commands support optional `json` argument for raw JSON output (default is human-readable table).

### Network Dashboard

Comprehensive view of all network stats (Health, Devices, Clients, Networks, DPI, etc.):

```bash
bash scripts/dashboard.sh
bash scripts/dashboard.sh json  # Raw JSON for all sections
```

**Output:** Full ASCII dashboard with all metrics.

### List Devices

Shows all UniFi devices (APs, switches, gateway):

```bash
bash scripts/devices.sh
bash scripts/devices.sh json  # Raw JSON
```

**Output:** Device name, model, IP, state, uptime, connected clients

### List Active Clients

Shows who's currently connected:

```bash
bash scripts/clients.sh
bash scripts/clients.sh json  # Raw JSON
```

**Output:** Hostname, IP, MAC, AP, signal strength, RX/TX rates

### Health Summary

Site-wide health status:

```bash
bash scripts/health.sh
bash scripts/health.sh json  # Raw JSON
```

**Output:** Subsystem status (WAN, LAN, WLAN), counts (up/adopted/disconnected)

### Top Applications (DPI)

Top bandwidth consumers by application:

```bash
bash scripts/top-apps.sh
bash scripts/top-apps.sh 15  # Show top 15 (default: 10)
```

**Output:** App name, category, RX/TX/total traffic in GB

### Recent Alerts

Recent alarms and events:

```bash
bash scripts/alerts.sh
bash scripts/alerts.sh 50  # Show last 50 (default: 20)
```

**Output:** Timestamp, alarm key, message, affected device

## Workflow

When the user asks about UniFi:

1. **"What's on my network?"** → Run `bash scripts/devices.sh` + `bash scripts/clients.sh`
2. **"Is everything healthy?"** → Run `bash scripts/health.sh`
3. **"Any problems?"** → Run `bash scripts/alerts.sh`
4. **"What's using bandwidth?"** → Run `bash scripts/top-apps.sh`
5. **"Show me a dashboard"** or general checkup → Run `bash scripts/dashboard.sh`

Always confirm the output looks reasonable before presenting it to the user (check for auth failures, empty data, etc.).

## Notes

- Requires network access to your UniFi gateway
- Uses UniFi OS login + `/proxy/network` API path
- All calls are **read-only GET requests**
- Tested endpoints are documented in `references/unifi-readonly-endpoints.md`

## Reference

- [Tested Endpoints](references/unifi-readonly-endpoints.md) — Full catalog of verified read-only API calls on your Cloud Gateway Max
