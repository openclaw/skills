#!/usr/bin/env bash
# UniFi site health summary
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/unifi-api.sh"

FORMAT="${1:-table}"

data=$(unifi_get "/api/s/$UNIFI_SITE/stat/health")

if [ "$FORMAT" = "json" ]; then
  echo "$data"
else
  # Table format
  echo "$data" | jq -r '
    ["SUBSYSTEM", "STATUS", "# UP", "# ADOPTED", "# DISCONNECTED"],
    ["---------", "------", "----", "---------", "--------------"],
    (.data[] | [
      .subsystem,
      .status,
      (.num_user // .num_ap // .num_sw // .num_gw // 0 | tostring),
      (.num_adopted // 0 | tostring),
      (.num_disconnected // 0 | tostring)
    ]) | @tsv
  ' | column -t -s $'\t'
fi
