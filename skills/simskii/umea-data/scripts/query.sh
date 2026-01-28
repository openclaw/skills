#!/bin/bash
# Query Umeå kommun open data API

set -e

DATASET_ID="$1"
LIMIT="${2:-20}"
BASE_URL="https://opendata.umea.se/api/v2"

if [ -z "$DATASET_ID" ]; then
    echo "Usage: $0 <dataset_id> [limit]"
    echo ""
    echo "Common datasets:"
    echo "  gop_lekparker                    - Playgrounds"
    echo "  laddplatser                      - EV charging stations"
    echo "  badplatser                       - Swimming spots"
    echo "  vandringsleder                   - Hiking trails"
    echo "  wifi-hotspots                    - WiFi hotspots"
    echo "  bygglov-beslut                   - Building permit decisions"
    echo "  bygglov-inkomna-arenden          - Building permit applications"
    echo "  trad-som-forvaltas-av-gator-och-parker - Trees"
    echo "  rastplatser                      - Rest areas"
    echo "  befolkningsfoeraendringar-helar  - Population changes"
    echo "  bostadsbestand-hustyp            - Housing stock by type"
    echo "  vaxthusgasutslapp_umea           - Greenhouse gas emissions"
    echo "  exempel-brottsstatistik-anmaelda-brott-fran-bra-s-oeppna-data - Crime statistics"
    echo ""
    echo "Example: $0 badplatser 10"
    exit 1
fi

# Query the API
curl -s "${BASE_URL}/catalog/datasets/${DATASET_ID}/records?limit=${LIMIT}" | jq '.'
