#!/usr/bin/env bash
#
# Devialet Phantom Speaker Control
# Requires: curl, jq (optional for pretty output)
#
# Usage: devialet.sh <host> <command> [args]
#        devialet.sh discover
#
# Commands:
#   status    - Show speaker/system info
#   play      - Start/resume playback
#   pause     - Pause playback
#   volume    - Get volume, or set if value provided (0-100)
#   up        - Volume up (default step: 5)
#   down      - Volume down (default step: 5)
#   mute      - Mute speakers
#   unmute    - Unmute speakers
#   sources   - List available sources
#   source    - Switch to source by ID
#   discover  - Find Devialet speakers on network
#

set -euo pipefail

# Handle help before anything else
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" || "${1:-}" == "help" ]]; then
    cat << 'EOF'
Devialet Phantom Speaker Control

Usage: devialet.sh <host> <command> [args]
       devialet.sh discover

Commands:
  status          Show speaker info
  play            Start/resume playback
  pause           Pause playback
  volume [0-100]  Get or set volume
  up              Volume up
  down            Volume down
  mute            Mute speakers
  unmute          Unmute speakers
  sources         List available sources
  source <id>     Switch to source

Environment:
  DEVIALET_HOST   Default speaker IP/hostname

Examples:
  devialet.sh 192.168.1.50 status
  devialet.sh 192.168.1.50 volume 40
  devialet.sh 192.168.1.50 play
  devialet.sh discover
EOF
    exit 0
fi

# Use DEVIALET_HOST as default if set
HOST="${1:-${DEVIALET_HOST:-}}"
CMD="${2:-status}"
ARG="${3:-}"

BASE_URL="http://${HOST}:80/ipcontrol/v1"

# Check for jq, use cat if not available
if command -v jq &>/dev/null; then
    FORMAT="jq ."
else
    FORMAT="cat"
fi

usage() {
    echo "Error: $1"
    echo "Run '$0 --help' for usage"
    exit 1
}

discover() {
    echo "Searching for Devialet speakers..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS: use dns-sd
        echo "(Press Ctrl+C after a few seconds)"
        dns-sd -B _http._tcp 2>/dev/null | grep -i "phantom\|devialet" || echo "No speakers found (or dns-sd timed out)"
    elif command -v avahi-browse &>/dev/null; then
        # Linux: use avahi
        timeout 5 avahi-browse -r _http._tcp 2>/dev/null | grep -i "phantom\|devialet" || echo "No speakers found"
    else
        echo "Install avahi-utils (Linux) for mDNS discovery"
        echo "Or check your router for devices named Phantom* or Devialet*"
    fi
}

get() {
    curl -s -H 'Content-Type:' -X GET "${BASE_URL}$1" | $FORMAT
}

post() {
    local endpoint="$1"
    local data="${2:-{}}"
    curl -s -H 'Content-Type: application/json' -X POST -d "$data" "${BASE_URL}${endpoint}" | $FORMAT
}

# Handle discover command specially (no host required)
if [[ "$HOST" == "discover" ]]; then
    discover
    exit 0
fi

# Validate host
if [[ -z "$HOST" ]]; then
    usage "No host specified. Set DEVIALET_HOST or pass host as first argument."
fi

case "$CMD" in
    status)
        echo "=== Device Info ==="
        get "/devices/current"
        echo ""
        echo "=== System Info ==="
        get "/systems/current"
        echo ""
        echo "=== Current Source ==="
        get "/groups/current/sources/current"
        ;;
    
    play)
        echo "Playing..."
        post "/groups/current/sources/current/playback/play"
        ;;
    
    pause)
        echo "Pausing..."
        post "/groups/current/sources/current/playback/pause"
        ;;
    
    volume)
        if [[ -z "$ARG" ]]; then
            # Get current volume
            get "/groups/current/sources/current/soundControl/volume"
        else
            # Set volume
            if [[ "$ARG" -lt 0 || "$ARG" -gt 100 ]]; then
                echo "Error: Volume must be 0-100"
                exit 1
            fi
            echo "Setting volume to ${ARG}..."
            post "/systems/current/sources/current/soundControl/volume" "{\"volume\": $ARG}"
        fi
        ;;
    
    up)
        echo "Volume up..."
        post "/groups/current/sources/current/soundControl/volumeUp"
        ;;
    
    down)
        echo "Volume down..."
        post "/groups/current/sources/current/soundControl/volumeDown"
        ;;
    
    mute)
        echo "Muting..."
        post "/groups/current/sources/current/playback/mute"
        ;;
    
    unmute)
        echo "Unmuting..."
        post "/groups/current/sources/current/playback/unmute"
        ;;
    
    sources)
        echo "Available sources:"
        get "/groups/current/sources"
        ;;
    
    source)
        if [[ -z "$ARG" ]]; then
            echo "Error: Source ID required"
            echo "Use 'sources' command to list available source IDs"
            exit 1
        fi
        echo "Switching to source ${ARG}..."
        post "/groups/current/sources/${ARG}/playback/play"
        ;;
    
    *)
        usage "Unknown command: $CMD"
        ;;
esac
