---
name: overseerr
description: Request movies/TV and monitor request status via the Overseerr API (stable Overseerr, not the beta Seerr rewrite).
homepage: https://overseerr.dev/
metadata: {"clawdbot":{"emoji":"🍿","requires":{"bins":["node"],"env":["OVERSEERR_URL","OVERSEERR_API_KEY"]},"primaryEnv":"OVERSEERR_API_KEY"}}
---

# Overseerr

Interact with a local/self-hosted Overseerr instance (search + request + status).

Note: This skill targets **Overseerr** (the current stable project), not the newer "Seerr" rewrite that is in beta.

## Setup

Set env vars (recommended via your Clawdbot config):

- `OVERSEERR_URL` (example: `http://localhost:5055`)
- `OVERSEERR_API_KEY` (Settings → General → API Key)

## Search

```bash
node {baseDir}/scripts/search.mjs "the matrix"
node {baseDir}/scripts/search.mjs "bluey" --type tv
node {baseDir}/scripts/search.mjs "dune" --limit 5
```

## Request

```bash
# movie
node {baseDir}/scripts/request.mjs "Dune" --type movie

# tv (optionally all seasons, default)
node {baseDir}/scripts/request.mjs "Bluey" --type tv --seasons all

# request specific seasons
node {baseDir}/scripts/request.mjs "Severance" --type tv --seasons 1,2

# 4K request
node {baseDir}/scripts/request.mjs "Oppenheimer" --type movie --is4k
```

## Status

```bash
node {baseDir}/scripts/requests.mjs --filter pending
node {baseDir}/scripts/requests.mjs --filter processing --limit 20
node {baseDir}/scripts/request-by-id.mjs 123
```

## Monitor (polling)

```bash
node {baseDir}/scripts/monitor.mjs --interval 30 --filter pending
```

Notes:
- This skill uses `X-Api-Key` auth.
- Overseerr can also push updates via webhooks; polling is a simple baseline.
