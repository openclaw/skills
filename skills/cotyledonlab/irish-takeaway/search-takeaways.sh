#!/bin/bash
# Search for takeaways near a location in Ireland
# Usage: ./search-takeaways.sh [location_name] [cuisine] [radius_m]
#
# Examples:
#   ./search-takeaways.sh drogheda
#   ./search-takeaways.sh dublin pizza 2000
#   ./search-takeaways.sh cork chinese 3000

set -e

# Default values
LOCATION=$(echo "${1:-drogheda}" | tr '[:upper:]' '[:lower:]')
CUISINE="${2:-takeaway}"
RADIUS="${3:-3000}"

# Get coordinates for location
case "$LOCATION" in
  drogheda)  LAT=53.7179; LNG=-6.3561 ;;
  dublin)    LAT=53.3498; LNG=-6.2603 ;;
  cork)      LAT=51.8985; LNG=-8.4756 ;;
  galway)    LAT=53.2707; LNG=-9.0568 ;;
  limerick)  LAT=52.6638; LNG=-8.6267 ;;
  waterford) LAT=52.2593; LNG=-7.1101 ;;
  dundalk)   LAT=54.0048; LNG=-6.4027 ;;
  swords)    LAT=53.4597; LNG=-6.2181 ;;
  navan)     LAT=53.6528; LNG=-6.6814 ;;
  bray)      LAT=53.2009; LNG=-6.0987 ;;
  *)
    echo "Unknown location: $LOCATION"
    echo "Known locations: drogheda, dublin, cork, galway, limerick, waterford, dundalk, swords, navan, bray"
    exit 1
    ;;
esac

echo "🍕 Searching for '$CUISINE' near $LOCATION (${LAT}, ${LNG})..."
echo ""

# Check for API key
if [ -z "$GOOGLE_PLACES_API_KEY" ]; then
  echo "❌ GOOGLE_PLACES_API_KEY not set"
  exit 1
fi

# Run search
goplaces search "$CUISINE" --lat="$LAT" --lng="$LNG" --radius-m="$RADIUS" --limit=10 --open-now 2>/dev/null || \
goplaces search "$CUISINE" --lat="$LAT" --lng="$LNG" --radius-m="$RADIUS" --limit=10
