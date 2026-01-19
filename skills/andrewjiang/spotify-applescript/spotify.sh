#!/bin/bash
# Spotify AppleScript Control Wrapper
set -euo pipefail

# Convert Spotify URL to URI if needed
convert_to_uri() {
    local input="$1"
    
    # Already a spotify: URI
    if [[ "$input" =~ ^spotify: ]]; then
        echo "$input"
        return
    fi
    
    # Extract from open.spotify.com URL
    if [[ "$input" =~ open\.spotify\.com/([a-z]+)/([a-zA-Z0-9]+) ]]; then
        local type="${BASH_REMATCH[1]}"
        local id="${BASH_REMATCH[2]}"
        echo "spotify:${type}:${id}"
        return
    fi
    
    # Return as-is
    echo "$input"
}

# Main command handler
case "${1:-}" in
    play)
        if [[ -z "${2:-}" ]]; then
            echo "Usage: spotify play <uri|url>"
            exit 1
        fi
        uri=$(convert_to_uri "$2")
        osascript -e "tell application \"Spotify\" to play track \"$uri\""
        ;;
    
    pause|playpause)
        osascript -e 'tell application "Spotify" to playpause'
        ;;
    
    next)
        osascript -e 'tell application "Spotify" to next track'
        ;;
    
    prev|previous)
        osascript -e 'tell application "Spotify" to previous track'
        ;;
    
    status)
        osascript -e 'tell application "Spotify"
            try
                set trackName to name of current track
                set artistName to artist of current track
                set albumName to album of current track
                set playerState to player state as string
                set vol to sound volume as integer
                return playerState & " | " & trackName & " - " & artistName & " | " & albumName & " | Vol: " & vol & "%"
            on error
                return "No track playing"
            end try
        end tell'
        ;;
    
    volume)
        if [[ -z "${2:-}" ]]; then
            # Get current volume
            osascript -e 'tell application "Spotify" to sound volume'
        else
            # Set volume (0-100)
            osascript -e "tell application \"Spotify\" to set sound volume to $2"
        fi
        ;;
    
    mute)
        osascript -e 'tell application "Spotify" to set sound volume to 0'
        ;;
    
    unmute)
        osascript -e 'tell application "Spotify" to set sound volume to 70'
        ;;
    
    state)
        osascript -e 'tell application "Spotify" to player state'
        ;;
    
    info)
        osascript -e 'tell application "Spotify"
            set trackName to name of current track
            set artistName to artist of current track
            set albumName to album of current track
            set trackDuration to duration of current track
            set trackPosition to player position
            set playerState to player state as string
            set isShuffling to shuffling as string
            set isRepeating to repeating as string
            return "Track: " & trackName & "\nArtist: " & artistName & "\nAlbum: " & albumName & "\nPosition: " & trackPosition & "s / " & (trackDuration / 1000) & "s\nState: " & playerState & "\nShuffle: " & isShuffling & "\nRepeat: " & isRepeating
        end tell'
        ;;
    
    *)
        cat <<EOF
Spotify AppleScript Control

Usage: spotify <command> [args]

Commands:
  play <uri|url>    Play track/album/playlist/episode
  pause             Toggle play/pause
  next              Next track
  prev              Previous track
  status            Show current track
  info              Show detailed track info
  state             Show player state (playing/paused)
  volume [0-100]    Get or set volume
  mute              Mute
  unmute            Unmute

Examples:
  spotify play spotify:playlist:665eC1myDA8iSepZ0HOZdG
  spotify play https://open.spotify.com/episode/5yJKH11UlF3sS3gcKKaUYx
  spotify pause
  spotify next
  spotify volume 75
  spotify status
EOF
        exit 1
        ;;
esac
