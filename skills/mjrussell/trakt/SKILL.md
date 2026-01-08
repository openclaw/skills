---
name: trakt
description: Track and view your watched movies and TV shows via trakt.tv. Use when user asks about their watch history, what they've been watching, or wants to search for movies/shows.
homepage: https://trakt.tv
metadata:
  clawdbot:
    emoji: "🎬"
    requires:
      bins: ["trakt-cli"]
---

# Trakt CLI

Query your trakt.tv watch history and search for movies/TV shows.

## Installation

```bash
npm install -g trakt-cli
```

## Setup

1. Create an app at https://trakt.tv/oauth/applications/new
2. Run: `trakt-cli auth --client-id <id> --client-secret <secret>`
3. Visit the URL shown and enter the device code
4. Credentials saved to `~/.trakt.yaml`

## Commands

### Watch History

```bash
trakt-cli history                  # Recent history (default: 10 items)
trakt-cli history --limit 25       # Show more
trakt-cli history --page 2         # Paginate
```

### Search

```bash
trakt-cli search "Breaking Bad"
trakt-cli search "The Matrix"
```

## Usage Examples

**User: "What have I been watching lately?"**
```bash
trakt-cli history
```

**User: "Show me my last 20 watched items"**
```bash
trakt-cli history --limit 20
```

**User: "Find info about Severance"**
```bash
trakt-cli search "Severance"
```

## Notes

- Search works without authentication
- History requires authentication
- Read-only access to watch history
