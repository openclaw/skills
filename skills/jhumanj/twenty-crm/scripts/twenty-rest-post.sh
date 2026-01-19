#!/bin/bash
set -euo pipefail

# Usage: twenty-rest-post.sh "/companies" '{"name":"Acme"}'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/twenty-config.sh"

PATH_PART="${1:-}"
JSON_BODY="${2:-}"

if [ -z "$PATH_PART" ] || [ -z "$JSON_BODY" ]; then
  echo "Usage: twenty-rest-post.sh \"/path\" '{...json...}'" >&2
  exit 1
fi

curl -sS -X POST "$TWENTY_BASE_URL/rest${PATH_PART}" \
  -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data "$JSON_BODY"
