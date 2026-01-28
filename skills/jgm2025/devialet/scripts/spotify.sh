#!/usr/bin/env bash
#
# Spotify Control for Devialet Speakers
# Requires: curl, jq
#
# Setup: Run with 'auth' to authenticate, then 'devices' to find your speaker
#
# Usage:
#   spotify.sh auth                    - Start OAuth flow
#   spotify.sh devices                 - List available devices
#   spotify.sh search "artist - track" - Search for a track
#   spotify.sh play "artist - track" [device_id] - Search and play
#   spotify.sh play-uri <spotify:track:xxx> [device_id] - Play specific URI
#   spotify.sh pause [device_id]       - Pause playback
#   spotify.sh resume [device_id]      - Resume playback
#   spotify.sh volume <0-100> [device_id] - Set volume
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/clawdbot"
SPOTIFY_CREDS="$CONFIG_DIR/spotify.json"
SPOTIFY_TOKEN="$CONFIG_DIR/spotify_token.json"

# Load credentials
load_creds() {
    if [[ ! -f "$SPOTIFY_CREDS" ]]; then
        echo "Error: Spotify credentials not found at $SPOTIFY_CREDS"
        echo "Create it with: {\"client_id\": \"xxx\", \"client_secret\": \"xxx\"}"
        exit 1
    fi
    CLIENT_ID=$(jq -r '.client_id' "$SPOTIFY_CREDS")
    CLIENT_SECRET=$(jq -r '.client_secret' "$SPOTIFY_CREDS")
}

# Get valid access token (refresh if needed)
get_token() {
    if [[ ! -f "$SPOTIFY_TOKEN" ]]; then
        echo "Error: Not authenticated. Run: $0 auth"
        exit 1
    fi
    
    local expires_at=$(jq -r '.expires_at // 0' "$SPOTIFY_TOKEN")
    local now=$(date +%s)
    
    if [[ $now -ge $expires_at ]]; then
        # Token expired, refresh it
        load_creds
        local refresh_token=$(jq -r '.refresh_token' "$SPOTIFY_TOKEN")
        
        local response=$(curl -s -X POST "https://accounts.spotify.com/api/token" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "grant_type=refresh_token&refresh_token=$refresh_token&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET")
        
        if echo "$response" | jq -e '.access_token' &>/dev/null; then
            local access_token=$(echo "$response" | jq -r '.access_token')
            local expires_in=$(echo "$response" | jq -r '.expires_in')
            local new_refresh=$(echo "$response" | jq -r '.refresh_token // empty')
            
            # Update token file
            jq --arg at "$access_token" \
               --arg ea "$((now + expires_in - 60))" \
               --arg rt "${new_refresh:-$refresh_token}" \
               '.access_token = $at | .expires_at = ($ea | tonumber) | .refresh_token = $rt' \
               "$SPOTIFY_TOKEN" > "${SPOTIFY_TOKEN}.tmp" && mv "${SPOTIFY_TOKEN}.tmp" "$SPOTIFY_TOKEN"
        else
            echo "Error refreshing token: $response"
            exit 1
        fi
    fi
    
    jq -r '.access_token' "$SPOTIFY_TOKEN"
}

# OAuth authentication flow
auth() {
    load_creds
    mkdir -p "$CONFIG_DIR"
    
    local REDIRECT_URI="http://localhost:8888/callback"
    local SCOPES="user-read-playback-state user-modify-playback-state user-read-currently-playing"
    local AUTH_URL="https://accounts.spotify.com/authorize?client_id=$CLIENT_ID&response_type=code&redirect_uri=$(printf %s "$REDIRECT_URI" | jq -sRr @uri)&scope=$(printf %s "$SCOPES" | jq -sRr @uri)"
    
    echo "Opening browser for Spotify authorization..."
    echo ""
    echo "If browser doesn't open, visit:"
    echo "$AUTH_URL"
    echo ""
    
    # Try to open browser
    xdg-open "$AUTH_URL" 2>/dev/null || open "$AUTH_URL" 2>/dev/null || echo "(Please open the URL manually)"
    
    echo "After authorizing, you'll be redirected to localhost:8888"
    echo "Paste the FULL redirect URL here (including ?code=...):"
    read -r callback_url
    
    # Extract code from URL
    local code=$(echo "$callback_url" | grep -oP 'code=\K[^&]+' || echo "$callback_url")
    
    if [[ -z "$code" ]]; then
        echo "Error: Could not extract authorization code"
        exit 1
    fi
    
    # Exchange code for token
    local response=$(curl -s -X POST "https://accounts.spotify.com/api/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "grant_type=authorization_code&code=$code&redirect_uri=$REDIRECT_URI&client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET")
    
    if echo "$response" | jq -e '.access_token' &>/dev/null; then
        local now=$(date +%s)
        local expires_in=$(echo "$response" | jq -r '.expires_in')
        echo "$response" | jq --arg ea "$((now + expires_in - 60))" '. + {expires_at: ($ea | tonumber)}' > "$SPOTIFY_TOKEN"
        echo "✓ Authenticated successfully!"
        echo "Token saved to $SPOTIFY_TOKEN"
    else
        echo "Error: $response"
        exit 1
    fi
}

# List available devices
devices() {
    local token=$(get_token)
    curl -s -X GET "https://api.spotify.com/v1/me/player/devices" \
        -H "Authorization: Bearer $token" | jq '.devices[] | {id: .id, name: .name, type: .type, is_active: .is_active}'
}

# Search for a track
search() {
    local query="$1"
    local token=$(get_token)
    local encoded_query=$(printf %s "$query" | jq -sRr @uri)
    
    curl -s -X GET "https://api.spotify.com/v1/search?q=$encoded_query&type=track&limit=5" \
        -H "Authorization: Bearer $token" | jq '.tracks.items[] | {name: .name, artist: .artists[0].name, uri: .uri, album: .album.name}'
}

# Play a track (search and play first result)
play() {
    local query="$1"
    local device_id="${2:-}"
    local token=$(get_token)
    
    # Search for track
    local encoded_query=$(printf %s "$query" | jq -sRr @uri)
    local track_uri=$(curl -s -X GET "https://api.spotify.com/v1/search?q=$encoded_query&type=track&limit=1" \
        -H "Authorization: Bearer $token" | jq -r '.tracks.items[0].uri // empty')
    
    if [[ -z "$track_uri" ]]; then
        echo "No track found for: $query"
        exit 1
    fi
    
    local track_name=$(curl -s -X GET "https://api.spotify.com/v1/search?q=$encoded_query&type=track&limit=1" \
        -H "Authorization: Bearer $token" | jq -r '.tracks.items[0] | "\(.name) by \(.artists[0].name)"')
    
    echo "Playing: $track_name"
    
    # Build URL with device_id if provided
    local url="https://api.spotify.com/v1/me/player/play"
    [[ -n "$device_id" ]] && url="$url?device_id=$device_id"
    
    curl -s -X PUT "$url" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{\"uris\": [\"$track_uri\"]}"
    
    echo "✓ Started playback"
}

# Play specific URI
play_uri() {
    local uri="$1"
    local device_id="${2:-}"
    local token=$(get_token)
    
    local url="https://api.spotify.com/v1/me/player/play"
    [[ -n "$device_id" ]] && url="$url?device_id=$device_id"
    
    curl -s -X PUT "$url" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{\"uris\": [\"$uri\"]}"
    
    echo "✓ Playing $uri"
}

# Pause playback
pause() {
    local device_id="${1:-}"
    local token=$(get_token)
    
    local url="https://api.spotify.com/v1/me/player/pause"
    [[ -n "$device_id" ]] && url="$url?device_id=$device_id"
    
    curl -s -X PUT "$url" -H "Authorization: Bearer $token"
    echo "✓ Paused"
}

# Resume playback
resume() {
    local device_id="${1:-}"
    local token=$(get_token)
    
    local url="https://api.spotify.com/v1/me/player/play"
    [[ -n "$device_id" ]] && url="$url?device_id=$device_id"
    
    curl -s -X PUT "$url" -H "Authorization: Bearer $token"
    echo "✓ Resumed"
}

# Set volume
volume() {
    local vol="$1"
    local device_id="${2:-}"
    local token=$(get_token)
    
    local url="https://api.spotify.com/v1/me/player/volume?volume_percent=$vol"
    [[ -n "$device_id" ]] && url="$url&device_id=$device_id"
    
    curl -s -X PUT "$url" -H "Authorization: Bearer $token"
    echo "✓ Volume set to $vol%"
}

# Main
CMD="${1:-help}"
shift || true

case "$CMD" in
    auth)
        auth
        ;;
    devices)
        devices
        ;;
    search)
        search "$1"
        ;;
    play)
        play "$@"
        ;;
    play-uri)
        play_uri "$@"
        ;;
    pause)
        pause "$@"
        ;;
    resume)
        resume "$@"
        ;;
    volume)
        volume "$@"
        ;;
    *)
        echo "Spotify Control for Devialet"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  auth                     - Authenticate with Spotify"
        echo "  devices                  - List available devices"
        echo "  search \"query\"           - Search for tracks"
        echo "  play \"artist - track\"    - Search and play"
        echo "  play-uri <uri>           - Play specific Spotify URI"
        echo "  pause                    - Pause playback"
        echo "  resume                   - Resume playback"
        echo "  volume <0-100>           - Set volume"
        echo ""
        echo "Setup:"
        echo "  1. Create $CONFIG_DIR/spotify.json with:"
        echo "     {\"client_id\": \"xxx\", \"client_secret\": \"xxx\"}"
        echo "  2. Run: $0 auth"
        ;;
esac
