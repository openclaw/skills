#!/bin/bash
set -euo pipefail

# Usage: twenty-rest-delete.sh "/companies/<id>" [destroy]
# If second arg is "destroy", calls the /destroy endpoint.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/twenty-config.sh"

PATH_PART="${1:-}"
MODE="${2:-}"

if [ -z "$PATH_PART" ]; then
  echo "Usage: twenty-rest-delete.sh \"/path\" [destroy]" >&2
  exit 1
fi

URL="$TWENTY_BASE_URL/rest${PATH_PART}"
if [ "$MODE" = "destroy" ]; then
  URL="$URL/destroy"
fi

curl -sS -X DELETE "$URL" \
  -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Accept: application/json"
