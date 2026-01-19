#!/bin/bash
set -euo pipefail

# Usage: twenty-graphql.sh 'query { companies(limit: 5) { totalCount } }' [variablesJson]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}" )" && pwd)"
# shellcheck disable=SC1091
source "$SCRIPT_DIR/twenty-config.sh"

QUERY="${1:-}"
VARIABLES="${2:-}"

if [ -z "$QUERY" ]; then
  echo "Usage: twenty-graphql.sh 'query { ... }' [variablesJson]" >&2
  exit 1
fi

QUERY_JSON=$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$QUERY")

if [ -n "$VARIABLES" ]; then
  BODY=$(printf '{"query":%s,"variables":%s}' "$QUERY_JSON" "$VARIABLES")
else
  BODY=$(printf '{"query":%s}' "$QUERY_JSON")
fi

curl -sS -X POST "$TWENTY_BASE_URL/graphql" \
  -H "Authorization: Bearer $TWENTY_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --data "$BODY"
