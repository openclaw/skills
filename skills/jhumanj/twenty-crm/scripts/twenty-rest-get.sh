#!/bin/bash
set -euo pipefail

# Usage: twenty-rest-get.sh "/companies" [queryString]
# Example: twenty-rest-get.sh "/companies" 'limit=10&offset=0'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/twenty-config.sh"

PATH_PART="${1:-}"
QUERY="${2:-}"

if [ -z "$PATH_PART" ]; then
  echo "Usage: twenty-rest-get.sh \"/path\" [queryString]" >&2
  exit 1
fi

URL="$TWENTY_BASE_URL/rest${PATH_PART}"
if [ -n "$QUERY" ]; then
  URL="$URL?$QUERY"
fi

curl -sS "$URL" \
  -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Accept: application/json"
