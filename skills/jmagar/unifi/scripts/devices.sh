#!/usr/bin/env bash
# List UniFi devices (APs, switches, gateway)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/unifi-api.sh"

FORMAT="${1:-table}"

data=$(unifi_get "/api/s/$UNIFI_SITE/stat/device")

if [ "$FORMAT" = "json" ]; then
  echo "$data"
else
  # Table format
  echo "$data" | jq -r '
    ["NAME", "MODEL", "IP", "STATE", "UPTIME", "CLIENTS"],
    ["----", "-----", "--", "-----", "------", "-------"],
    (.data[] | [
      .name // .mac,
      .model,
      .ip,
      .state_name // .state,
      (.uptime | if . then (. / 3600 | floor | tostring) + "h" else "N/A" end),
      (.num_sta // 0 | tostring)
    ]) | @tsv
  ' | column -t -s $'\t'
fi
