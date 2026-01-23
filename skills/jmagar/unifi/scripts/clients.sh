#!/usr/bin/env bash
# List active UniFi clients
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/unifi-api.sh"

FORMAT="${1:-table}"

data=$(unifi_get "/api/s/$UNIFI_SITE/stat/sta")

if [ "$FORMAT" = "json" ]; then
  echo "$data"
else
  # Table format
  echo "$data" | jq -r '
    ["HOSTNAME", "IP", "MAC", "AP", "SIGNAL", "RX/TX (Mbps)"],
    ["--------", "--", "---", "--", "------", "------------"],
    (.data[] | [
      (.hostname // .name // "Unknown"),
      .ip,
      .mac,
      (.ap_mac // "N/A")[0:17],
      ((.signal // 0 | tostring) + " dBm"),
      (((.rx_rate // 0) / 1000 | floor | tostring) + "/" + ((.tx_rate // 0) / 1000 | floor | tostring))
    ]) | @tsv
  ' | column -t -s $'\t'
fi
