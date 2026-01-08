#!/bin/bash
# Get elevator outages at Wiener Linien stations
# Usage: ./elevators.sh [line]
#
# Example: ./elevators.sh       (all elevator outages)
# Example: ./elevators.sh U6    (U6 only)

if [ -n "$1" ]; then
    URL="https://www.wienerlinien.at/ogd_realtime/trafficInfoList?name=aufzugsinfo&relatedLine=$1"
else
    URL="https://www.wienerlinien.at/ogd_realtime/trafficInfoList?name=aufzugsinfo"
fi

curl -s "$URL" | jq '
  .data.trafficInfos // [] | map({
    station: .attributes.station,
    location: .attributes.location,
    status: .attributes.status,
    reason: .attributes.reason,
    lines: .relatedLines,
    towards: .attributes.towards
  })
'
