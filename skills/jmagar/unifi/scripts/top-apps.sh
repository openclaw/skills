#!/usr/bin/env bash
# Top applications by traffic (DPI)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/unifi-api.sh"

LIMIT="${1:-10}"

data=$(unifi_get "/api/s/$UNIFI_SITE/stat/sitedpi")

echo "$data" | jq -r --argjson limit "$LIMIT" '
  ["APP", "CATEGORY", "RX (GB)", "TX (GB)", "TOTAL (GB)"],
  ["---", "--------", "-------", "-------", "----------"],
  (.data[0].by_app // [] 
   | sort_by(-.tx_bytes + -.rx_bytes) 
   | .[:$limit][] 
   | [
      .app,
      .cat,
      ((.rx_bytes // 0) / 1073741824 | . * 100 | floor / 100 | tostring),
      ((.tx_bytes // 0) / 1073741824 | . * 100 | floor / 100 | tostring),
      (((.rx_bytes // 0) + (.tx_bytes // 0)) / 1073741824 | . * 100 | floor / 100 | tostring)
    ]
  ) | @tsv
' | column -t -s $'\t'
