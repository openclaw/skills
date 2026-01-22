---
name: spotify-web-api
description: Spotify control via Web API - playback, history, top tracks, search. Cross-platform (no Mac required).
homepage: https://spotify.com
metadata: {"clawdbot":{"emoji":"🎵","requires":{"env":["SPOTIFY_CLIENT_ID","SPOTIFY_CLIENT_SECRET"]}}}
---

# Spotify Web API (Cross-Platform)

Control Spotify via Web API. Works from any platform — no Mac required.

## Setup

### 1. Create Spotify App:

1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Add redirect URI: `http://localhost:8888/callback`
4. Copy **Client ID** and **Client Secret**

### 2. Set Environment Variables:

```bash
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
```

### 3. Authenticate:

```bash
python3 {baseDir}/scripts/spotify.py auth
```

Opens browser for OAuth. Token cached in `~/.spotify_cache.json`.

## Commands

```bash
# Currently playing
python3 {baseDir}/scripts/spotify.py now

# Recently played
python3 {baseDir}/scripts/spotify.py recent

# Top tracks/artists
python3 {baseDir}/scripts/spotify.py top tracks --period month
python3 {baseDir}/scripts/spotify.py top artists --period year

# Playback control
python3 {baseDir}/scripts/spotify.py play
python3 {baseDir}/scripts/spotify.py play "bohemian rhapsody"
python3 {baseDir}/scripts/spotify.py pause
python3 {baseDir}/scripts/spotify.py next
python3 {baseDir}/scripts/spotify.py prev

# Search
python3 {baseDir}/scripts/spotify.py search "daft punk"

# List devices
python3 {baseDir}/scripts/spotify.py devices
```

## Example Chat Usage

- "What am I listening to?"
- "What have I listened to lately?"
- "What are my top tracks this month?"
- "Play Bohemian Rhapsody"
- "Skip this song"
- "Pause the music"

## Requirements

- Spotify Premium (for playback control)
- Free accounts can still view history/top tracks

## API Reference

Uses the Spotify Web API:
https://developer.spotify.com/documentation/web-api
