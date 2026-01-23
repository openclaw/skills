---
name: spotify-history
description: Access Spotify listening history, top artists/tracks, and get personalized recommendations via the Spotify Web API. Use when fetching a user's recent plays, analyzing music taste, or generating recommendations. Requires one-time OAuth setup.
---

# Spotify History & Recommendations

Access Spotify listening history and get personalized recommendations.

## Setup (One-Time)

### 1. Create Spotify Developer App

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Click **Create App** (or use existing app)
3. Fill in:
   - **App name:** `Clawd` (or any name)
   - **App description:** `Personal assistant integration`
   - **Redirect URI:** `http://127.0.0.1:8888/callback` ⚠️ Use IP, not localhost!
4. Save and note the **Client ID** and **Client Secret**

### 2. Store Credentials

```bash
# Set environment variables (add to ~/.zshrc or ~/.bashrc)
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
```

### 3. Authenticate

```bash
python3 scripts/spotify-auth.py
```

A browser opens for Spotify login. Authorize the app, and tokens are saved to `~/.config/spotify-clawd/token.json`.

## Usage

### Command Line

```bash
# Recent listening history
python3 scripts/spotify-api.py recent

# Top artists (time_range: short_term, medium_term, long_term)
python3 scripts/spotify-api.py top-artists medium_term

# Top tracks
python3 scripts/spotify-api.py top-tracks medium_term

# Get recommendations based on your top artists
python3 scripts/spotify-api.py recommend

# Raw API call (any endpoint)
python3 scripts/spotify-api.py json /me
python3 scripts/spotify-api.py json /me/player/recently-played
```

### Time Ranges

- `short_term` — approximately last 4 weeks
- `medium_term` — approximately last 6 months (default)
- `long_term` — all time

### Example Output

```
Top Artists (medium_term):
  1. Hans Zimmer [soundtrack, score]
  2. John Williams [soundtrack, score]
  3. Michael Giacchino [soundtrack, score]
  4. Max Richter [ambient, modern classical]
  5. Ludovico Einaudi [italian contemporary classical]
```

## Agent Usage

When user asks about music:
- "What have I been listening to?" → `spotify-api.py recent`
- "Who are my top artists?" → `spotify-api.py top-artists`
- "Recommend new music" → `spotify-api.py recommend` + add your own knowledge

For recommendations, combine API data with music knowledge to suggest similar artists not in their library.

## Token Refresh

Tokens auto-refresh when expired. If issues occur:
1. Delete `~/.config/spotify-clawd/token.json`
2. Re-run `spotify-auth.py`

## Security Notes

- Tokens stored with 0600 permissions (user-only read/write)
- Client secret should be kept private
- Redirect URI uses `127.0.0.1` (local only) for security

## Required Scopes

- `user-read-recently-played` — recent listening history
- `user-top-read` — top artists and tracks
- `user-read-playback-state` — current playback
- `user-read-currently-playing` — currently playing track
