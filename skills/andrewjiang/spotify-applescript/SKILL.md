---
name: spotify-applescript
description: Control Spotify desktop app via AppleScript. Play playlists, tracks, albums, episodes, and manage playback. Works reliably with macOS Spotify app without API keys or OAuth.
homepage: https://github.com/andrewjiang/HoloClawd-Open-Firmware
metadata: {"clawdbot":{"emoji":"🎵","os":["darwin"]}}
triggers:
  - spotify
  - play music
  - play playlist
  - play episode
  - pause music
  - next track
  - previous track
---

# Spotify AppleScript Control

Control the Spotify desktop app using AppleScript. Works reliably with the macOS Spotify app without API rate limits or OAuth.

## Requirements

- Spotify desktop app installed and running on macOS
- No setup required - just works

## Quick Start

```bash
# Play a playlist
spotify play "spotify:playlist:665eC1myDA8iSepZ0HOZdG"
spotify play "https://open.spotify.com/playlist/665eC1myDA8iSepZ0HOZdG"

# Play an episode
spotify play "spotify:episode:5yJKH11UlF3sS3gcKKaUYx"
spotify play "https://open.spotify.com/episode/5yJKH11UlF3sS3gcKKaUYx"

# Play a track
spotify play "spotify:track:7hQJA50XrCWABAu5v6QZ4i"

# Playback control
spotify pause          # Toggle play/pause
spotify next           # Next track
spotify prev           # Previous track
spotify status         # Current track info

# Volume control
spotify volume 50      # Set volume (0-100)
spotify mute           # Mute
spotify unmute         # Unmute
```

## Spotify CLI Wrapper

The `spotify` command is a wrapper script at `{baseDir}/spotify.sh`

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `play <uri>` | Play track/album/playlist/episode | `spotify play spotify:track:xxx` |
| `pause` | Toggle play/pause | `spotify pause` |
| `next` | Next track | `spotify next` |
| `prev` | Previous track | `spotify prev` |
| `status` | Show current track info | `spotify status` |
| `volume <0-100>` | Set volume | `spotify volume 75` |
| `mute` | Mute | `spotify mute` |
| `unmute` | Unmute | `spotify unmute` |

### URI Formats

Accepts both Spotify URIs and open.spotify.com URLs:

- `spotify:track:7hQJA50XrCWABAu5v6QZ4i`
- `https://open.spotify.com/track/7hQJA50XrCWABAu5v6QZ4i`
- `spotify:playlist:665eC1myDA8iSepZ0HOZdG`
- `https://open.spotify.com/playlist/665eC1myDA8iSepZ0HOZdG?si=xxx`
- `spotify:episode:5yJKH11UlF3sS3gcKKaUYx`
- `https://open.spotify.com/episode/5yJKH11UlF3sS3gcKKaUYx`
- `spotify:album:xxx`
- `spotify:artist:xxx`

The script auto-converts URLs to URIs.

## Direct AppleScript Commands

For more control, use AppleScript directly:

```bash
# Play
osascript -e 'tell application "Spotify" to play track "spotify:playlist:xxx"'

# Pause/Play toggle
osascript -e 'tell application "Spotify" to playpause'

# Next/Previous
osascript -e 'tell application "Spotify" to next track'
osascript -e 'tell application "Spotify" to previous track'

# Get current track
osascript -e 'tell application "Spotify"
  set trackName to name of current track
  set artistName to artist of current track
  return trackName & " by " & artistName
end tell'

# Get player state
osascript -e 'tell application "Spotify" to player state'

# Set volume (0-100)
osascript -e 'tell application "Spotify" to set sound volume to 75'

# Get current position (in seconds)
osascript -e 'tell application "Spotify" to player position'

# Set position (in seconds)
osascript -e 'tell application "Spotify" to set player position to 30'
```

## Available Properties

```applescript
tell application "Spotify"
  name of current track          -- Track name
  artist of current track        -- Artist name
  album of current track         -- Album name
  duration of current track      -- Duration in ms
  player position                -- Position in seconds
  player state                   -- playing/paused/stopped
  sound volume                   -- 0-100
  repeating                      -- true/false
  repeating enabled              -- true/false
  shuffling                      -- true/false
  shuffling enabled              -- true/false
end tell
```

## Examples

### Agent Usage

When the user says:
- "Play my power hour playlist" → extract playlist URI and run `spotify play <uri>`
- "Pause the music" → run `spotify pause`
- "Next track" → run `spotify next`
- "What's playing?" → run `spotify status`

### Play a specific episode

```bash
spotify play https://open.spotify.com/episode/5yJKH11UlF3sS3gcKKaUYx
```

### Get full track info

```bash
osascript -e 'tell application "Spotify"
  return "Track: " & (name of current track) & "\nArtist: " & (artist of current track) & "\nAlbum: " & (album of current track) & "\nState: " & (player state as string)
end tell'
```

## Installation

The skill is self-contained. To make the `spotify` command available system-wide:

```bash
chmod +x {baseDir}/spotify.sh
sudo ln -sf {baseDir}/spotify.sh /usr/local/bin/spotify
```

Or add the skill directory to PATH.

## Troubleshooting

**"Spotify got an error"**
- Make sure Spotify desktop app is running
- Spotify must be launched at least once to accept AppleScript commands

**Play command does nothing**
- Verify the URI format is correct
- Try playing from Spotify app first to ensure the content exists

**No audio**
- Check system volume and Spotify app volume
- Ensure correct output device is selected in Spotify preferences

## Limitations

- Requires Spotify desktop app to be running
- macOS only (uses AppleScript)
- Cannot search or browse library (use web interface or app for discovery)
- Cannot manage playlists (add/remove tracks)

For playlist management and search, use the web interface or consider the `spotify-player` skill (requires OAuth setup).
