#!/bin/bash
# Tabussen/Ultra Stop Lookup using ResRobot API
# Usage: ./search-location.sh <query> [limit]

set -e

# Configuration
API_KEY="${RESROBOT_API_KEY:-YOUR_API_KEY_HERE}"
BASE_URL="https://api.resrobot.se/v2.1/location.name"

# Arguments
QUERY="$1"
LIMIT="${2:-5}"

# Validation
if [ -z "$QUERY" ]; then
    echo "Usage: $0 <query> [limit]"
    echo ""
    echo "Arguments:"
    echo "  query  - Location name to search for (append ? for fuzzy search)"
    echo "  limit  - Number of results (default: 5, max: 10)"
    echo ""
    echo "Examples:"
    echo "  $0 'Umeå Vasaplan'      # Exact search"
    echo "  $0 'Vasaplan?'          # Fuzzy search"
    echo "  $0 'universitet?' 10    # Fuzzy search, 10 results"
    exit 1
fi

if [ "$API_KEY" = "YOUR_API_KEY_HERE" ]; then
    echo "ERROR: Please set RESROBOT_API_KEY environment variable"
    echo "Get your API key at: https://developer.trafiklab.se"
    exit 1
fi

# Ensure limit is within bounds
if [ "$LIMIT" -gt 10 ]; then
    LIMIT=10
fi

# URL encode the query
ENCODED_QUERY=$(echo -n "$QUERY" | jq -sRr @uri)

# Make API request
RESPONSE=$(curl -s "${BASE_URL}?input=${ENCODED_QUERY}&maxNo=${LIMIT}&format=json&accessId=${API_KEY}")

# Check for errors
if echo "$RESPONSE" | jq -e '.errorCode' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.errorText // "Unknown error"')
    echo "API Error: $ERROR_MSG"
    exit 1
fi

# Parse and display results
STOP_COUNT=$(echo "$RESPONSE" | jq '.stopLocationOrCoordLocation | length // 0')

if [ "$STOP_COUNT" -eq 0 ]; then
    echo "No locations found for: $QUERY"
    echo ""
    echo "Tips:"
    echo "  - Check spelling (Swedish: å, ä, ö)"
    echo "  - Try fuzzy search by adding ? to query"
    echo "  - Add city name (e.g., 'Storgatan, Umeå?')"
    exit 0
fi

echo "========================================"
echo "SEARCH RESULTS FOR: $QUERY"
echo "========================================"
echo ""

echo "$RESPONSE" | jq -r '
.stopLocationOrCoordLocation[]? | 
select(.StopLocation) |
.StopLocation |
"ID: \(.extId)
Name: \(.name)
Coordinates: \(.lat), \(.lon)
Weight: \(.weight)
----------------------------------------"
'

echo ""
echo "Found $STOP_COUNT location(s)"
echo ""
echo "Use the ID in journey search:"
echo "  ./journey.sh <from-id> <to-id> [datetime] [mode]"
