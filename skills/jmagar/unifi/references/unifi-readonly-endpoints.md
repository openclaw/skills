# UniFi Local Gateway (UniFi OS / UCG Max) — Read-Only API Calls (Best-Effort)

This is a **best-effort** catalog of *read-only* endpoints commonly available on UniFi OS gateways (UDM/UDR/UCG Max) running the UniFi Network application.

## Base Paths (UCG Max / UniFi OS)

After logging in to UniFi OS (`POST /api/auth/login`), the Network app API is typically accessed via:

- `https://<gateway>/proxy/network/api/...`

Most “controller-style” endpoints below assume:

- **Site**: `default`
- **Prefix**: `/proxy/network` (UniFi OS difference)

So, for example:

- `GET https://<gateway>/proxy/network/api/s/default/stat/health`

## UniFi OS (console-level) endpoints (read-only)

These are not site-scoped.

- `GET /status` — basic gateway status (only endpoint often reachable without auth)
- `GET /api/users/self` (aka `/api/self` on older controllers) — logged-in user
- `GET /api/self/sites` — list sites
- `GET /api/stat/sites` — sites + health/alerts summary
- `GET /api/stat/admin` — admins + permissions (requires sufficient rights)

## Network app endpoints (site-scoped, GET-only reads)

All of these are under `/api/s/{site}/...` (remember to prefix with `/proxy/network` on UniFi OS).

### Identity / meta
- `GET /api/s/{site}/self` — logged-in user (site context)
- `GET /api/s/{site}/stat/sysinfo` — controller + site high-level info
- `GET /api/s/{site}/stat/ccode` — country codes
- `GET /api/s/{site}/stat/current-channel` — available RF channels

### Health / monitoring
- `GET /api/s/{site}/stat/health` — health overview
- `GET /api/s/{site}/stat/event` — recent events (newest-first, often ~3000 cap)
- `GET /api/s/{site}/stat/alarm` — recent alarms (newest-first, often ~3000 cap)

### Clients
- `GET /api/s/{site}/stat/sta` — **active** clients
- `GET /api/s/{site}/rest/user` — **known/configured** clients

### Devices
- `GET /api/s/{site}/stat/device-basic` — minimal device info (mac/type/state)
- `GET /api/s/{site}/stat/device` — full device list
- `GET /api/s/{site}/stat/device/{mac}` — UniFi OS variant for a single device by mac (UDM/UCG)

### Routing / WAN
- `GET /api/s/{site}/stat/routing` — active routes
- `GET /api/s/{site}/stat/dynamicdns` — DynamicDNS status

### Wireless / RF
- `GET /api/s/{site}/stat/rogueap` — neighboring/rogue APs
- `GET /api/s/{site}/stat/spectrumscan` — RF scan results (optionally per-device)

### DPI / traffic (read-only when used with GET)
- `GET /api/s/{site}/stat/sitedpi` — site-wide DPI stats (apps/categories)
- `GET /api/s/{site}/stat/stadpi` — per-client DPI stats

### Port forwards
- `GET /api/s/{site}/rest/portforward` — configured port forwards

### Profiles / config (treat as read-only by using GET)
These *can* be writable via PUT/POST in general, but are safe if you only **GET**.

- `GET /api/s/{site}/rest/setting` — site settings
- `GET /api/s/{site}/rest/networkconf` — networks
- `GET /api/s/{site}/rest/wlanconf` — WLANs
- `GET /api/s/{site}/rest/wlanconf/{_id}` — WLAN details
- `GET /api/s/{site}/rest/firewallrule` — user firewall rules
- `GET /api/s/{site}/rest/firewallgroup` — firewall groups
- `GET /api/s/{site}/rest/routing` — user-defined routes (read)
- `GET /api/s/{site}/rest/dynamicdns` — DynamicDNS config
- `GET /api/s/{site}/rest/portconf` — switch port profiles
- `GET /api/s/{site}/rest/radiusprofile` — RADIUS profiles
- `GET /api/s/{site}/rest/account` — RADIUS accounts

## Notes / caveats

- UniFi’s local API is largely **undocumented** and varies by Network app version.
- Some endpoints support POST “filters” (e.g., `stat/device` filter by macs). Those can still be read-only, but we should treat *all POSTs as suspicious* unless we confirm they don’t mutate state.
- For a Clawdbot skill, safest posture is:
  - Use **GET-only** to the `stat/*` and selected `rest/*` endpoints
  - Avoid anything under `/cmd/*` and any `PUT/POST/DELETE`

## Tested On Your Gateway

Tested against your UniFi OS gateway on `10.1.0.1` using the UniFi OS login + `/proxy/network` path.

| Group | Path | HTTP | OK | Note |
|---|---|---:|:--:|---|
| console | `/status` | 200 | ✅ | 200 |
| console | `/api/users/self` | 200 | ✅ | 200 |
| console | `/api/self/sites` | 404 | ❌ | http 404 |
| console | `/api/stat/sites` | 404 | ❌ | http 404 |
| console | `/api/stat/admin` | 404 | ❌ | http 404 |
| network | `/api/s/default/self` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/sysinfo` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/ccode` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/current-channel` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/health` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/event` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/alarm` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/sta` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/user` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/device-basic` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/device` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/routing` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/dynamicdns` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/rogueap` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/spectrumscan` | 404 | ❌ | api.err.NotFound |
| network | `/api/s/default/stat/sitedpi` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/stat/stadpi` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/portforward` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/setting` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/networkconf` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/wlanconf` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/firewallrule` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/firewallgroup` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/routing` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/dynamicdns` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/portconf` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/radiusprofile` | 200 | ✅ | meta.rc=ok |
| network | `/api/s/default/rest/account` | 200 | ✅ | meta.rc=ok |

## Source
- Community reverse-engineered list (includes UniFi OS notes): https://ubntwiki.com/products/software/unifi-controller/api
