#!/usr/bin/env bash
# Simple wrapper to call v6.bvg.transport.rest /journeys and pretty-print results
# Usage: ./journeys.sh "from query or stop id" "to query or stop id" "arrival|departure" "2026-01-29T17:50:00+01:00"
set -euo pipefail
from_raw="$1"
to_raw="$2"
mode="$3" # arrival or departure
when="$4"

base="https://v6.bvg.transport.rest"

# Helper: url-encode
urlencode() { python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1], safe=''))" "$1"; }

from_enc=$(urlencode "$from_raw")
to_enc=$(urlencode "$to_raw")

if [[ "$mode" == "arrival" ]]; then
  q="/journeys?from=${from_enc}&to=${to_enc}&arrival=${when}&results=3&stopovers=true"
else
  q="/journeys?from=${from_enc}&to=${to_enc}&departure=${when}&results=3&stopovers=true"
fi

url="$base$q"

curl -s "$url" | jq '.journeys[] | {duration,transfers,legs: [.legs[] | {origin:.origin.name,destination:.destination.name,departure:.departure,arrival:.arrival,line:.line.name,walk:.walk}]} '
