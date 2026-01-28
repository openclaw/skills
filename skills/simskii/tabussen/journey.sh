#!/bin/bash
# Tabussen/Ultra Journey Planner using ResRobot API
# Usage: ./journey.sh <from-id> <to-id> [datetime] [mode]

set -e

# Configuration
API_KEY="${RESROBOT_API_KEY:-YOUR_API_KEY_HERE}"
BASE_URL="https://api.resrobot.se/v2.1/trip"

# Arguments
FROM_ID="$1"
TO_ID="$2"
DATETIME="$3"
MODE="${4:-depart}"  # "depart" or "arrive"

# Validation
if [ -z "$FROM_ID" ] || [ -z "$TO_ID" ]; then
    echo "Usage: $0 <from-id> <to-id> [datetime] [mode]"
    echo ""
    echo "Arguments:"
    echo "  from-id   - Origin stop ID or coordinates (lat#lon)"
    echo "  to-id     - Destination stop ID or coordinates (lat#lon)"
    echo "  datetime  - Optional: '18:30', 'tomorrow 09:00', '2026-01-28 14:00'"
    echo "  mode      - Optional: 'depart' (default) or 'arrive'"
    echo ""
    echo "Examples:"
    echo "  $0 740066252 740025841                      # Now"
    echo "  $0 740066252 740025841 '08:30'              # Today 08:30"
    echo "  $0 740066252 740025841 'tomorrow 09:00'     # Tomorrow"
    echo "  $0 740066252 740025841 '18:00' arrive       # Arrive by 18:00"
    echo "  $0 '63.825#20.263' 740025841                # From coordinates"
    exit 1
fi

if [ "$API_KEY" = "YOUR_API_KEY_HERE" ]; then
    echo "ERROR: Please set RESROBOT_API_KEY environment variable"
    echo "Get your API key at: https://developer.trafiklab.se"
    exit 1
fi

# Build query parameters
PARAMS="format=json&accessId=${API_KEY}&passlist=1&numF=5"

# Handle origin (ID or coordinates)
if [[ "$FROM_ID" == *"#"* ]]; then
    # Coordinates format: lat#lon
    ORIGIN_LAT=$(echo "$FROM_ID" | cut -d'#' -f1)
    ORIGIN_LON=$(echo "$FROM_ID" | cut -d'#' -f2)
    PARAMS="${PARAMS}&originCoordLat=${ORIGIN_LAT}&originCoordLong=${ORIGIN_LON}"
else
    PARAMS="${PARAMS}&originId=${FROM_ID}"
fi

# Handle destination (ID or coordinates)
if [[ "$TO_ID" == *"#"* ]]; then
    # Coordinates format: lat#lon
    DEST_LAT=$(echo "$TO_ID" | cut -d'#' -f1)
    DEST_LON=$(echo "$TO_ID" | cut -d'#' -f2)
    PARAMS="${PARAMS}&destCoordLat=${DEST_LAT}&destCoordLong=${DEST_LON}"
else
    PARAMS="${PARAMS}&destId=${TO_ID}"
fi

# Parse datetime
if [ -n "$DATETIME" ]; then
    # Handle "tomorrow" keyword
    if [[ "$DATETIME" == tomorrow* ]]; then
        TOMORROW=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "tomorrow" +%Y-%m-%d)
        TIME_PART=$(echo "$DATETIME" | sed 's/tomorrow //')
        if [ -n "$TIME_PART" ] && [ "$TIME_PART" != "tomorrow" ]; then
            PARAMS="${PARAMS}&date=${TOMORROW}&time=${TIME_PART}"
        else
            PARAMS="${PARAMS}&date=${TOMORROW}"
        fi
    # Handle full date format YYYY-MM-DD HH:MM
    elif [[ "$DATETIME" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2} ]]; then
        DATE_PART=$(echo "$DATETIME" | cut -d' ' -f1)
        TIME_PART=$(echo "$DATETIME" | cut -d' ' -f2)
        PARAMS="${PARAMS}&date=${DATE_PART}"
        if [ -n "$TIME_PART" ]; then
            PARAMS="${PARAMS}&time=${TIME_PART}"
        fi
    # Handle time only HH:MM
    elif [[ "$DATETIME" =~ ^[0-9]{2}:[0-9]{2}$ ]]; then
        PARAMS="${PARAMS}&time=${DATETIME}"
    fi
fi

# Handle arrive mode
if [ "$MODE" = "arrive" ]; then
    PARAMS="${PARAMS}&searchForArrival=1"
fi

# Make API request
RESPONSE=$(curl -s "${BASE_URL}?${PARAMS}")

# Check for errors
if echo "$RESPONSE" | jq -e '.errorCode' > /dev/null 2>&1; then
    ERROR_MSG=$(echo "$RESPONSE" | jq -r '.errorText // "Unknown error"')
    echo "API Error: $ERROR_MSG"
    exit 1
fi

# Check for trips
TRIP_COUNT=$(echo "$RESPONSE" | jq '.Trip | length // 0')

if [ "$TRIP_COUNT" -eq 0 ]; then
    echo "No journeys found"
    echo ""
    echo "Tips:"
    echo "  - Check that both stop IDs are valid"
    echo "  - Try a different time (some routes have limited frequency)"
    echo "  - Late night service may be limited"
    exit 0
fi

# Display planning period info
PERIOD_BEGIN=$(echo "$RESPONSE" | jq -r '.Trip[0].ServiceDays[0].planningPeriodBegin // "N/A"')
PERIOD_END=$(echo "$RESPONSE" | jq -r '.Trip[0].ServiceDays[0].planningPeriodEnd // "N/A"')

echo "========================================"
echo "JOURNEY OPTIONS"
echo "========================================"
echo "Planning period: $PERIOD_BEGIN to $PERIOD_END"
echo ""

# Process each trip
OPTION_NUM=0
echo "$RESPONSE" | jq -c '.Trip[]' | while read -r TRIP; do
    OPTION_NUM=$((OPTION_NUM + 1))
    
    # Get origin and destination from first and last leg
    ORIGIN_NAME=$(echo "$TRIP" | jq -r '.LegList.Leg[0].Origin.name')
    DEST_NAME=$(echo "$TRIP" | jq -r '.LegList.Leg[-1].Destination.name')
    
    # Get departure and arrival times
    DEPART_TIME=$(echo "$TRIP" | jq -r '.LegList.Leg[0].Origin.time')
    DEPART_DATE=$(echo "$TRIP" | jq -r '.LegList.Leg[0].Origin.date')
    ARRIVE_TIME=$(echo "$TRIP" | jq -r '.LegList.Leg[-1].Destination.time')
    ARRIVE_DATE=$(echo "$TRIP" | jq -r '.LegList.Leg[-1].Destination.date')
    
    # Count transfers (legs - 1, excluding walks)
    LEG_COUNT=$(echo "$TRIP" | jq '[.LegList.Leg[] | select(.type == "JNY")] | length')
    TRANSFERS=$((LEG_COUNT - 1))
    if [ "$TRANSFERS" -lt 0 ]; then
        TRANSFERS=0
    fi
    
    # Get duration
    DURATION=$(echo "$TRIP" | jq -r '.duration // "N/A"')
    # Convert ISO duration to readable format
    DURATION_READABLE=$(echo "$DURATION" | sed 's/PT//' | sed 's/H/h /' | sed 's/M/m/')
    
    echo "=============================================================="
    echo "OPTION $OPTION_NUM: $ORIGIN_NAME -> $DEST_NAME"
    echo "=============================================================="
    echo "Date:     $DEPART_DATE"
    echo "Depart:   $DEPART_TIME"
    echo "Arrive:   $ARRIVE_TIME"
    echo "Duration: $DURATION_READABLE"
    echo "Changes:  $TRANSFERS"
    echo ""
    echo "LEGS:"
    
    # Process each leg
    echo "$TRIP" | jq -c '.LegList.Leg[]' | while read -r LEG; do
        LEG_TYPE=$(echo "$LEG" | jq -r '.type')
        LEG_NAME=$(echo "$LEG" | jq -r '.name // "Walking"')
        
        ORIG_NAME=$(echo "$LEG" | jq -r '.Origin.name')
        ORIG_TIME=$(echo "$LEG" | jq -r '.Origin.time')
        DEST_NAME_LEG=$(echo "$LEG" | jq -r '.Destination.name')
        DEST_TIME=$(echo "$LEG" | jq -r '.Destination.time')
        
        if [ "$LEG_TYPE" = "WALK" ]; then
            DISTANCE=$(echo "$LEG" | jq -r '.dist // "unknown"')
            echo "  -> WALK ${DISTANCE}m"
            echo "     From: $ORIG_TIME $ORIG_NAME"
            echo "     To:   $DEST_TIME $DEST_NAME_LEG"
        else
            DIRECTION=$(echo "$LEG" | jq -r '.direction // "N/A"')
            # Product can be object or array, handle both
            OPERATOR=$(echo "$LEG" | jq -r 'if .Product | type == "array" then .Product[0].operator else .Product.operator end // "N/A"')
            TRANSPORT_NUM=$(echo "$LEG" | jq -r '.transportNumber // ""')
            TRANSPORT_CAT=$(echo "$LEG" | jq -r '.transportCategory // ""')
            
            echo "  -> $TRANSPORT_CAT $LEG_NAME"
            echo "     Operator: $OPERATOR"
            echo "     From: $ORIG_TIME $ORIG_NAME"
            echo "     To:   $DEST_TIME $DEST_NAME_LEG"
            echo "     Direction: $DIRECTION"
            
            # Show intermediate stops if available
            STOP_COUNT=$(echo "$LEG" | jq 'if .Stops.Stop then (.Stops.Stop | length) else 0 end')
            if [ "$STOP_COUNT" -gt 2 ]; then
                echo "     Stops: $STOP_COUNT (including start/end)"
            fi
        fi
        echo ""
    done
    
    echo ""
done

echo "========================================"
echo "Found $TRIP_COUNT journey option(s)"
