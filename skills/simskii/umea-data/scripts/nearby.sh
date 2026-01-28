#!/bin/bash
# Find nearest locations from Umeå kommun data given coordinates

set -e

DATASET_ID="$1"
LAT="$2"
LON="$3"
LIMIT="${4:-10}"
BASE_URL="https://opendata.umea.se/api/v2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$DATASET_ID" ] || [ -z "$LAT" ] || [ -z "$LON" ]; then
    echo "Usage: $0 <dataset_id> <latitude> <longitude> [limit]"
    echo ""
    echo "Find nearest locations to given coordinates."
    echo ""
    echo "Example:"
    echo "  $0 gop_lekparker 63.8200 20.3000 5"
    echo "  (Find 5 nearest playgrounds to Mariehem)"
    echo ""
    echo "  $0 laddplatser 63.8258 20.2630 3"
    echo "  (Find 3 nearest EV charging stations to city center)"
    echo ""
    echo "Common coordinates in Umeå:"
    echo "  City center:      63.8258, 20.2630"
    echo "  Mariehem:         63.8200, 20.3000"
    echo "  Universum/Campus: 63.8190, 20.3070"
    echo "  Teg:              63.8400, 20.2300"
    echo "  Holmsund:         63.7100, 20.3700"
    exit 1
fi

echo "Finding nearest locations in ${DATASET_ID} to coordinates (${LAT}, ${LON})..."
echo ""

curl -s "${BASE_URL}/catalog/datasets/${DATASET_ID}/records?limit=100" | \
jq --arg lat "$LAT" --arg lon "$LON" --argjson limit "$LIMIT" -f "${SCRIPT_DIR}/distance.jq"
