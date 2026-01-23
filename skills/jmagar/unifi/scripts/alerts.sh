#!/usr/bin/env bash
# Recent UniFi alarms/alerts
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/unifi-api.sh"

LIMIT="${1:-20}"

data=$(unifi_get "/api/s/$UNIFI_SITE/stat/alarm")

echo "$data" | jq -r --argjson limit "$LIMIT" '
  ["TIME", "KEY", "MESSAGE", "AP/DEVICE"],
  ["----", "---", "-------", "----------"],
  (.data[:$limit][] | [
    (.datetime | strftime("%Y-%m-%d %H:%M")),
    .key,
    (.msg // "N/A"),
    (.ap_name // .gw_name // .sw_name // "N/A")
  ]) | @tsv
' | column -t -s $'\t'
