#!/usr/bin/env bash
set -euo pipefail

# Reflect API helper script
# Usage:
#   reflect.sh daily "text" ["list_name"]
#   reflect.sh note "subject" "content_markdown"
#   reflect.sh link "url" "title" ["description"]
#   reflect.sh links

# Configuration: Set these environment variables
# REFLECT_TOKEN    - Your Reflect API access token (required)
# REFLECT_GRAPH_ID - Your graph ID (required, find via /api/graphs endpoint)

# Check for required environment variables
if [[ -z "${REFLECT_TOKEN:-}" ]]; then
  echo "Error: REFLECT_TOKEN environment variable not set" >&2
  echo "Get your token at: https://reflect.app/developer/oauth" >&2
  exit 1
fi

if [[ -z "${REFLECT_GRAPH_ID:-}" ]]; then
  echo "Error: REFLECT_GRAPH_ID environment variable not set" >&2
  echo "Find your graph ID by running:" >&2
  echo "  curl -H \"Authorization: Bearer \$REFLECT_TOKEN\" https://reflect.app/api/graphs" >&2
  exit 1
fi

API_BASE="https://reflect.app/api/graphs/$REFLECT_GRAPH_ID"

case "${1:-help}" in
  daily)
    TEXT="${2:?Usage: reflect.sh daily \"text\" [\"list_name\"]}"
    LIST_NAME="${3:-}"
    
    PAYLOAD=$(jq -n \
      --arg text "$TEXT" \
      --arg list "$LIST_NAME" \
      '{
        text: $text,
        transform_type: "list-append"
      } + (if $list != "" then {list_name: $list} else {} end)')
    
    curl -s -X PUT "$API_BASE/daily-notes" \
      -H "Authorization: Bearer $REFLECT_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD"
    ;;
    
  note)
    SUBJECT="${2:?Usage: reflect.sh note \"subject\" \"content_markdown\" [pinned]}"
    CONTENT="${3:?Usage: reflect.sh note \"subject\" \"content_markdown\" [pinned]}"
    PINNED="${4:-false}"
    
    curl -s -X POST "$API_BASE/notes" \
      -H "Authorization: Bearer $REFLECT_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$(jq -n \
        --arg subject "$SUBJECT" \
        --arg content "$CONTENT" \
        --argjson pinned "$PINNED" \
        '{subject: $subject, content_markdown: $content, pinned: $pinned}')"
    ;;
    
  link)
    URL="${2:?Usage: reflect.sh link \"url\" \"title\" [\"description\"]}"
    TITLE="${3:?Usage: reflect.sh link \"url\" \"title\" [\"description\"]}"
    DESC="${4:-}"
    
    PAYLOAD=$(jq -n \
      --arg url "$URL" \
      --arg title "$TITLE" \
      --arg desc "$DESC" \
      '{url: $url, title: $title} + (if $desc != "" then {description: $desc} else {} end)')
    
    curl -s -X POST "$API_BASE/links" \
      -H "Authorization: Bearer $REFLECT_TOKEN" \
      -H "Content-Type: application/json" \
      -d "$PAYLOAD"
    ;;
    
  links)
    curl -s "$API_BASE/links" \
      -H "Authorization: Bearer $REFLECT_TOKEN" | jq .
    ;;
    
  books)
    curl -s "$API_BASE/books" \
      -H "Authorization: Bearer $REFLECT_TOKEN" | jq .
    ;;
    
  graphs)
    # Helper to find your graph ID
    curl -s "https://reflect.app/api/graphs" \
      -H "Authorization: Bearer $REFLECT_TOKEN" | jq .
    ;;
    
  *)
    echo "Reflect API Helper"
    echo ""
    echo "Setup:"
    echo "  export REFLECT_TOKEN=\"your-access-token\""
    echo "  export REFLECT_GRAPH_ID=\"your-graph-id\""
    echo ""
    echo "Usage:"
    echo "  reflect.sh daily \"text\" [\"[[List Name]]\"]  - Append to daily note"
    echo "  reflect.sh note \"subject\" \"markdown\"       - Create a new note"
    echo "  reflect.sh link \"url\" \"title\" [\"desc\"]     - Save a link"
    echo "  reflect.sh links                            - List saved links"
    echo "  reflect.sh books                            - List books"
    echo "  reflect.sh graphs                           - List your graphs (to find graph ID)"
    ;;
esac
