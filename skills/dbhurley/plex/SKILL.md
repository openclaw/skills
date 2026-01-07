---
name: plex
description: Control Plex Media Server - browse libraries, search, play media, manage playback.
homepage: https://plex.tv
metadata: {"clawdis":{"emoji":"🎬","requires":{"bins":["curl"],"env":["PLEX_TOKEN","PLEX_SERVER"]},"primaryEnv":"PLEX_TOKEN"}}
---

# Plex Media Server

Control Plex Media Server using the Plex API.

## Setup

Set environment variables:
- `PLEX_SERVER`: Your Plex server URL (e.g., `http://192.168.1.100:32400`)
- `PLEX_TOKEN`: Your Plex auth token (find it at plex.tv/claim or in Plex app XML)

## Common Commands

### Get Server Info
```bash
curl -s "$PLEX_SERVER/?X-Plex-Token=$PLEX_TOKEN" -H "Accept: application/json"
```

### Browse Libraries
```bash
curl -s "$PLEX_SERVER/library/sections?X-Plex-Token=$PLEX_TOKEN" -H "Accept: application/json"
```

### List Library Contents
```bash
# Replace 1 with your library section key (from browse above)
curl -s "$PLEX_SERVER/library/sections/1/all?X-Plex-Token=$PLEX_TOKEN" -H "Accept: application/json"
```

### Search
```bash
curl -s "$PLEX_SERVER/search?query=SEARCH_TERM&X-Plex-Token=$PLEX_TOKEN" -H "Accept: application/json"
```

### Get Recently Added
```bash
curl -s "$PLEX_SERVER/library/recentlyAdded?X-Plex-Token=$PLEX_TOKEN" -H "Accept: application/json"
```

### Get On Deck (Continue Watching)
```bash
curl -s "$PLEX_SERVER/library/onDeck?X-Plex-Token=$PLEX_TOKEN" -H "Accept: application/json"
```

### Get Active Sessions (What's Playing Now)
```bash
curl -s "$PLEX_SERVER/status/sessions?X-Plex-Token=$PLEX_TOKEN" -H "Accept: application/json"
```

### List Available Clients/Players
```bash
curl -s "$PLEX_SERVER/clients?X-Plex-Token=$PLEX_TOKEN" -H "Accept: application/json"
```

## Library Section Types

- Movies (usually section 1)
- TV Shows (usually section 2)
- Music
- Photos

## Notes

- Add `-H "Accept: application/json"` for JSON output (default is XML)
- Library section keys (1, 2, 3...) vary by server setup — list sections first
- Media keys look like `/library/metadata/12345`
- Always confirm before starting playback on a device
- Get your token: plex.tv → Account → Authorized Devices → XML link
