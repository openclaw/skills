#!/bin/bash
# Search Wiener Linien stops by name
# Usage: ./search-stop.sh <name>
#
# Returns: StopID (RBL), DIVA, StopText, Longitude, Latitude

QUERY="${1:-}"

if [ -z "$QUERY" ]; then
    echo "Usage: $0 <stop-name>"
    echo "Example: $0 stephansplatz"
    exit 1
fi

echo "Searching for stops matching: $QUERY"
echo "---"
echo "StopID;DIVA;StopText;Municipality;Longitude;Latitude"
curl -s "https://www.wienerlinien.at/ogd_realtime/doku/ogd/wienerlinien-ogd-haltepunkte.csv" | grep -i "$QUERY" | head -20
