#!/bin/bash
# Plan a trip with natural language locations
# Usage: ./trip.sh <from> <to> [datetime] [mode]
#
# Accepts location names, addresses, or coordinates - no IDs needed.
# Times are always Swedish local time (CET/CEST).
#
# Examples:
#   ./trip.sh "Malmö C" "Lund C"
#   ./trip.sh "Kalendegatan 12C" "Malmö C" "09:00"
#   ./trip.sh "Malmö C" "Copenhagen" "tomorrow 18:00"
#   ./trip.sh "55.605#13.003" "Malmö C"
#   ./trip.sh "Malmö Hyllie" "Amalienborg Slotsplads" "10:00"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SWEDISH_TZ="Europe/Stockholm"

FROM_INPUT="${1:-}"
TO_INPUT="${2:-}"
DATETIME="${3:-}"
MODE="${4:-depart}"

# Show usage
if [[ -z "$FROM_INPUT" ]] || [[ -z "$TO_INPUT" ]]; then
    cat <<'EOF'
Usage: ./trip.sh <from> <to> [datetime] [mode]

Arguments:
  from      Origin - station name, address, or coordinates (lat#lon)
  to        Destination - station name, address, or coordinates (lat#lon)
  datetime  Optional: "18:30", "tomorrow 09:00", "2026-01-15 09:00"
  mode      Optional: "depart" (default) or "arrive"

Examples:
  ./trip.sh "Malmö C" "Lund C"
  ./trip.sh "Kalendegatan 12C, Malmö" "Malmö C" "09:00"
  ./trip.sh "Malmö C" "Copenhagen" "tomorrow 18:00"
  ./trip.sh "55.605#13.003" "Malmö C"
EOF
    exit 1
fi

# Detect if input is coordinates (lat#lon format)
is_coordinates() {
    [[ "$1" =~ ^-?[0-9]+\.?[0-9]*#-?[0-9]+\.?[0-9]*$ ]]
}

# Search for a location and return best match
# Returns: ID|TYPE|NAME or error
# Note: For ADDRESS/POI types, returns coordinates as ID with LOCATION type
#       because the Journey API only supports STOP_AREA and LOCATION types
search_location() {
    local query="$1"
    local label="$2"  # "origin" or "destination"

    # If coordinates, return directly
    if is_coordinates "$query"; then
        echo "${query}|LOCATION|Coordinates (${query})"
        return 0
    fi

    # URL encode
    local encoded
    encoded=$(printf '%s' "$query" | jq -sRr @uri)

    # Make API call
    local response http_code
    http_code=$(curl -s --max-time 15 -w "%{http_code}" --compressed \
        "https://www.skanetrafiken.se/gw-tps/api/v2/Points?name=${encoded}" \
        -H "search-engine-environment: TjP" \
        -H "accept: application/json" \
        -H "user-agent: skanetrafiken-agent-skill/1.1" \
        -o /tmp/skanetrafiken_search_$$.json 2>/dev/null) || http_code="000"

    if [[ "$http_code" != "200" ]]; then
        rm -f /tmp/skanetrafiken_search_$$.json
        echo "ERROR: Failed to search for ${label}. Network error or API unavailable." >&2
        echo "RETRY: Check internet connection and try again." >&2
        return 1
    fi

    response=$(cat /tmp/skanetrafiken_search_$$.json)
    rm -f /tmp/skanetrafiken_search_$$.json

    # Check results
    local count
    count=$(echo "$response" | jq '.points | length')

    if [[ "$count" -eq 0 ]]; then
        echo "ERROR: No locations found for ${label}: '${query}'" >&2
        echo "SUGGESTIONS:" >&2
        echo "  - Check spelling (Swedish characters: å, ä, ö)" >&2
        echo "  - Try a more specific name (e.g., 'Malmö C' instead of 'Malmö')" >&2
        echo "  - For addresses, include city (e.g., 'Kalendegatan 12C, Malmö')" >&2
        echo "  - For Copenhagen, try 'Köpenhamn' or specific station name" >&2
        return 1
    fi

    # Get best match (first result)
    local id name type area lat lon
    id=$(echo "$response" | jq -r '.points[0].id2')
    name=$(echo "$response" | jq -r '.points[0].name')
    type=$(echo "$response" | jq -r '.points[0].type')
    area=$(echo "$response" | jq -r '.points[0].area // "Skåne"')
    lat=$(echo "$response" | jq -r '.points[0].lat // empty')
    lon=$(echo "$response" | jq -r '.points[0].lon // empty')

    # If multiple matches, show alternatives
    if [[ "$count" -gt 1 ]]; then
        echo "NOTE: Found ${count} matches for '${query}'. Using best match: ${name} (${type})" >&2
        if [[ "$count" -le 5 ]]; then
            echo "OTHER OPTIONS:" >&2
            echo "$response" | jq -r '.points[1:5][] | "  - \(.name) (\(.type)) - \(.area // "Skåne")"' >&2
        fi
        echo "" >&2
    fi

    # For ADDRESS and POI types, use coordinates with LOCATION type
    # The Journey API only supports STOP_AREA and LOCATION (coordinates)
    if [[ "$type" == "ADDRESS" || "$type" == "POI" ]] && [[ -n "$lat" ]] && [[ -n "$lon" ]]; then
        echo "${lat}#${lon}|LOCATION|${name}, ${area}"
    else
        echo "${id}|${type}|${name}, ${area}"
    fi
}

# Main execution
echo "Planning trip..."
echo ""

# Search for origin
echo "Searching for origin: ${FROM_INPUT}"
FROM_RESULT=$(search_location "$FROM_INPUT" "origin") || exit 1
IFS='|' read -r FROM_ID FROM_TYPE FROM_NAME <<< "$FROM_RESULT"
echo "  Found: ${FROM_NAME}"
echo ""

# Search for destination
echo "Searching for destination: ${TO_INPUT}"
TO_RESULT=$(search_location "$TO_INPUT" "destination") || exit 1
IFS='|' read -r TO_ID TO_TYPE TO_NAME <<< "$TO_RESULT"
echo "  Found: ${TO_NAME}"
echo ""

# Build journey parameters
echo "═══════════════════════════════════════════════════════════════"
echo "TRIP: ${FROM_NAME} → ${TO_NAME}"
if [[ -n "$DATETIME" ]]; then
    echo "TIME: ${DATETIME} (${MODE})"
else
    echo "TIME: Now"
fi
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Call journey.sh
JOURNEY_ARGS=("$FROM_ID" "$FROM_TYPE" "$TO_ID" "$TO_TYPE")
[[ -n "$DATETIME" ]] && JOURNEY_ARGS+=("$DATETIME")
[[ -n "$DATETIME" ]] && JOURNEY_ARGS+=("$MODE")

# Execute journey script
exec "$SCRIPT_DIR/journey.sh" "${JOURNEY_ARGS[@]}"
