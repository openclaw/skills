---
name: prowlarr
version: 1.0.0
description: Search indexers and manage Prowlarr. Use when the user asks to "search for a torrent", "search indexers", "find a release", "check indexer status", "list indexers", "prowlarr search", "sync indexers", or mentions Prowlarr/indexer management.
---

# Prowlarr Skill

Search across all your indexers and manage Prowlarr via API.

## Setup

Config: `~/.clawdbot/credentials/prowlarr/config.json`

```json
{
  "url": "https://prowlarr.example.com",
  "apiKey": "your-api-key"
}
```

Get your API key from: Prowlarr → Settings → General → Security → API Key

---

## Quick Reference

### Search Releases

```bash
# Basic search across all indexers
./scripts/prowlarr-api.sh search "ubuntu 22.04"

# Search torrents only
./scripts/prowlarr-api.sh search "ubuntu" --torrents

# Search usenet only
./scripts/prowlarr-api.sh search "ubuntu" --usenet

# Search specific categories (2000=Movies, 5000=TV, 3000=Audio, 7000=Books)
./scripts/prowlarr-api.sh search "inception" --category 2000

# TV search with TVDB ID
./scripts/prowlarr-api.sh tv-search --tvdb 71663 --season 1 --episode 1

# Movie search with IMDB ID
./scripts/prowlarr-api.sh movie-search --imdb tt0111161
```

### List Indexers

```bash
# All indexers
./scripts/prowlarr-api.sh indexers

# With status details
./scripts/prowlarr-api.sh indexers --verbose
```

### Indexer Health & Stats

```bash
# Usage stats per indexer
./scripts/prowlarr-api.sh stats

# Test all indexers
./scripts/prowlarr-api.sh test-all

# Test specific indexer
./scripts/prowlarr-api.sh test <indexer-id>
```

### Indexer Management

```bash
# Enable/disable an indexer
./scripts/prowlarr-api.sh enable <indexer-id>
./scripts/prowlarr-api.sh disable <indexer-id>

# Delete an indexer
./scripts/prowlarr-api.sh delete <indexer-id>
```

### App Sync

```bash
# Sync indexers to Sonarr/Radarr/etc
./scripts/prowlarr-api.sh sync

# List connected apps
./scripts/prowlarr-api.sh apps
```

### System

```bash
# System status
./scripts/prowlarr-api.sh status

# Health check
./scripts/prowlarr-api.sh health
```

---

## Search Categories

| ID | Category |
|----|----------|
| 2000 | Movies |
| 5000 | TV |
| 3000 | Audio |
| 7000 | Books |
| 1000 | Console |
| 4000 | PC |
| 6000 | XXX |

Sub-categories: 2010 (Movies/Foreign), 2020 (Movies/Other), 2030 (Movies/SD), 2040 (Movies/HD), 2045 (Movies/UHD), 2050 (Movies/BluRay), 2060 (Movies/3D), 5010 (TV/WEB-DL), 5020 (TV/Foreign), 5030 (TV/SD), 5040 (TV/HD), 5045 (TV/UHD), etc.

---

## Common Use Cases

**"Search for the latest Ubuntu ISO"**
```bash
./scripts/prowlarr-api.sh search "ubuntu 24.04"
```

**"Find Game of Thrones S01E01"**
```bash
./scripts/prowlarr-api.sh tv-search --tvdb 121361 --season 1 --episode 1
```

**"Search for Inception in 4K"**
```bash
./scripts/prowlarr-api.sh search "inception 2160p" --category 2045
```

**"Check if my indexers are healthy"**
```bash
./scripts/prowlarr-api.sh stats
./scripts/prowlarr-api.sh test-all
```

**"Push indexer changes to Sonarr/Radarr"**
```bash
./scripts/prowlarr-api.sh sync
```
