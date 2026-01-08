#!/bin/bash
# Get real-time departures from a Wiener Linien stop
# Usage: ./departures.sh <stop-id> [stop-id2] [stop-id3] ...
#
# Example: ./departures.sh 252 4116  (Stephansplatz platforms)

if [ -z "$1" ]; then
    echo "Usage: $0 <stop-id> [stop-id2] ..."
    echo ""
    echo "Find stop IDs with: ./search-stop.sh <name>"
    echo "Example: $0 252 4116"
    exit 1
fi

# Build stopId query params
PARAMS=""
for STOP_ID in "$@"; do
    PARAMS="${PARAMS}&stopId=${STOP_ID}"
done
# Remove leading &
PARAMS="${PARAMS:1}"

# Include all traffic info
URL="https://www.wienerlinien.at/ogd_realtime/monitor?${PARAMS}&activateTrafficInfo=stoerungkurz&activateTrafficInfo=stoerunglang&activateTrafficInfo=aufzugsinfo"

curl -s "$URL" | jq '
  .data.monitors[] | {
    stop: .locationStop.properties.title,
    rbl: .locationStop.properties.attributes.rbl,
    lines: [
      .lines[] | {
        line: .name,
        towards: .towards,
        type: .type,
        barrierFree: .barrierFree,
        nextDepartures: [.departures.departure[:5][] | {
          countdown: .departureTime.countdown,
          planned: .departureTime.timePlanned,
          real: .departureTime.timeReal
        }]
      }
    ]
  }
'
