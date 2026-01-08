#!/bin/bash
# Get current Wiener Linien disruptions
# Usage: ./disruptions.sh [line1] [line2] ...
#
# Example: ./disruptions.sh           (all disruptions)
# Example: ./disruptions.sh U1 U3     (U1 and U3 only)

# Build relatedLine query params
PARAMS=""
for LINE in "$@"; do
    PARAMS="${PARAMS}&relatedLine=${LINE}"
done

if [ -n "$PARAMS" ]; then
    # Remove leading &
    PARAMS="${PARAMS:1}"
    URL="https://www.wienerlinien.at/ogd_realtime/trafficInfoList?${PARAMS}"
else
    URL="https://www.wienerlinien.at/ogd_realtime/trafficInfoList"
fi

curl -s "$URL" | jq '
  .data.trafficInfos // [] | map({
    title: .title,
    description: .description,
    lines: .relatedLines,
    category: (
      if .refTrafficInfoCategoryId == 1 then "Elevator"
      elif .refTrafficInfoCategoryId == 2 then "Long disruption"
      elif .refTrafficInfoCategoryId == 3 then "Short disruption"
      else "Other"
      end
    ),
    time: .time,
    station: .attributes.station,
    status: .attributes.status
  })
'
