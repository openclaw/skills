#!/usr/bin/env bash
#
# Play a song on Devialet via Spotify
# Usage: play-on-devialet.sh "Artist - Song"
#        play-on-devialet.sh "spotify:track:xxx"
#        play-on-devialet.sh pause
#        play-on-devialet.sh resume
#        play-on-devialet.sh volume 50
#

set -euo pipefail

export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"

DEVIALET_IP="${DEVIALET_IP:-}"

if [[ -z "$DEVIALET_IP" ]]; then
    echo "Error: DEVIALET_IP not set. Set it with: export DEVIALET_IP=192.168.x.x"
    exit 1
fi
QUERY="${1:-}"
ARG2="${2:-}"

# Check Spotify is running
check_spotify() {
    if ! dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.freedesktop.DBus.Properties.Get string:'org.mpris.MediaPlayer2.Player' string:'PlaybackStatus' &>/dev/null; then
        echo "Error: Spotify not running. Start Spotify first."
        exit 1
    fi
}

# Search for track URI using web search (fallback)
search_track() {
    local query="$1"
    # Use a simple web search to find the Spotify track URL
    # This is a workaround since we don't have API access
    local encoded=$(printf %s "$query" | sed 's/ /%20/g')
    
    # Try to find via web search (returns empty if can't find)
    local result=$(curl -s "https://www.google.com/search?q=site:open.spotify.com+track+$encoded" \
        -H "User-Agent: Mozilla/5.0" 2>/dev/null | \
        grep -oP 'open\.spotify\.com/track/[a-zA-Z0-9]+' | head -1)
    
    if [[ -n "$result" ]]; then
        echo "spotify:track:${result##*/}"
    fi
}

# Play a track
play_track() {
    local input="$1"
    local uri=""
    
    # Check if it's already a Spotify URI
    if [[ "$input" == spotify:track:* ]]; then
        uri="$input"
    elif [[ "$input" == https://open.spotify.com/track/* ]]; then
        # Extract track ID from URL
        local track_id=$(echo "$input" | grep -oP 'track/\K[a-zA-Z0-9]+')
        uri="spotify:track:$track_id"
    else
        # It's a search query - open search in Spotify
        local encoded=$(printf %s "$input" | sed 's/ /%20/g')
        echo "Searching for: $input"
        dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.OpenUri string:"spotify:search:$encoded" &>/dev/null
        sleep 1
        # Try to play the first result using keyboard
        export DISPLAY=:0
        xdotool key Return 2>/dev/null || true
        sleep 0.5
    fi
    
    if [[ -n "$uri" ]]; then
        echo "Playing: $uri"
        dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 org.mpris.MediaPlayer2.Player.OpenUri string:"$uri" &>/dev/null
    fi
    
    sleep 1
    
    # Ensure Devialet is playing
    curl -s -X POST "http://$DEVIALET_IP/ipcontrol/v1/groups/current/sources/current/playback/play" &>/dev/null
    
    # Show what's playing
    sleep 1
    echo "Now playing: $(playerctl -p spotify metadata --format '{{artist}} - {{title}}' 2>/dev/null || echo 'unknown')"
}

# Main
case "${QUERY,,}" in
    pause|stop)
        check_spotify
        echo "Pausing..."
        curl -s -X POST "http://$DEVIALET_IP/ipcontrol/v1/groups/current/sources/current/playback/pause" &>/dev/null
        playerctl -p spotify pause 2>/dev/null || true
        echo "Paused"
        ;;
    
    resume|play)
        if [[ -z "$ARG2" ]]; then
            check_spotify
            echo "Resuming..."
            playerctl -p spotify play 2>/dev/null || true
            curl -s -X POST "http://$DEVIALET_IP/ipcontrol/v1/groups/current/sources/current/playback/play" &>/dev/null
            echo "Playing: $(playerctl -p spotify metadata --format '{{artist}} - {{title}}' 2>/dev/null)"
        else
            check_spotify
            play_track "$ARG2"
        fi
        ;;
    
    volume|vol)
        if [[ -n "$ARG2" ]]; then
            echo "Setting volume to $ARG2%"
            curl -s -X POST -H "Content-Type: application/json" \
                -d "{\"volume\": $ARG2}" \
                "http://$DEVIALET_IP/ipcontrol/v1/systems/current/sources/current/soundControl/volume" &>/dev/null
            echo "Volume: $ARG2%"
        else
            vol=$(curl -s "http://$DEVIALET_IP/ipcontrol/v1/groups/current/sources/current/soundControl/volume" | grep -oP '"volume":\s*\K\d+')
            echo "Current volume: $vol%"
        fi
        ;;
    
    status)
        check_spotify
        echo "=== Spotify ==="
        playerctl -p spotify metadata --format 'Track: {{artist}} - {{title}}
Album: {{album}}
Status: {{status}}'
        echo ""
        echo "=== Devialet ==="
        curl -s "http://$DEVIALET_IP/ipcontrol/v1/groups/current/sources/current" | \
            jq -r '"Source: \(.source.type // "none")\nState: \(.playingState)"'
        vol=$(curl -s "http://$DEVIALET_IP/ipcontrol/v1/groups/current/sources/current/soundControl/volume" | grep -oP '"volume":\s*\K\d+')
        echo "Volume: $vol%"
        ;;
    
    help|--help|-h|"")
        echo "Play music on Devialet via Spotify"
        echo ""
        echo "Usage:"
        echo "  $0 \"Artist - Song\"     Search and play"
        echo "  $0 spotify:track:xxx   Play specific track"
        echo "  $0 pause               Pause playback"
        echo "  $0 resume              Resume playback"
        echo "  $0 volume [0-100]      Get/set volume"
        echo "  $0 status              Show current status"
        ;;
    
    *)
        check_spotify
        play_track "$QUERY"
        ;;
esac
