---
name: radarr
version: 1.0.0
description: Search and add movies to Radarr. Supports collections, search-on-add option.
metadata: {"clawdbot":{"emoji":"🎬","requires":{"bins":["curl","jq"]}}}
---

# Radarr

Add movies to your Radarr library with collection support.

## Setup

Create `~/.clawdbot/credentials/radarr/config.json`:
```json
{
  "url": "http://localhost:7878",
  "apiKey": "your-api-key",
  "defaultQualityProfile": 1
}
```
- `defaultQualityProfile`: Quality profile ID (run `config` to see options)

## Workflow

1. **Search**: `search "Movie Name"` - returns numbered list
2. **Present results with TMDB links** - always show clickable links
3. **Check**: User picks a number
4. **Collection prompt**: If movie is part of collection, ask user
5. **Add**: Add movie or full collection

## Important
- **Always include TMDB links** when presenting search results to user
- Format: `[Title (Year)](https://themoviedb.org/movie/ID)`
- Uses `defaultQualityProfile` from config; can override per-add

## Commands

### Search for movies
```bash
bash scripts/radarr.sh search "Inception"
```

### Check if movie exists in library
```bash
bash scripts/radarr.sh exists <tmdbId>
```

### Add a movie (searches immediately by default)
```bash
bash scripts/radarr.sh add <tmdbId>           # searches right away
bash scripts/radarr.sh add <tmdbId> --no-search  # don't search
```

### Add full collection (searches immediately by default)
```bash
bash scripts/radarr.sh add-collection <collectionTmdbId>
bash scripts/radarr.sh add-collection <collectionTmdbId> --no-search
```

### Remove a movie
```bash
bash scripts/radarr.sh remove <tmdbId>              # keep files
bash scripts/radarr.sh remove <tmdbId> --delete-files  # delete files too
```
**Always ask user if they want to delete files when removing!**

### Get root folders & quality profiles (for config)
```bash
bash scripts/radarr.sh config
```
