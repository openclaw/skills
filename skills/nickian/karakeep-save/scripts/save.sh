#!/bin/bash
# Save a URL to Karakeep
# Usage: save.sh <url> [note]
#
# Requires environment variables:
#   KARAKEEP_URL - Your Karakeep instance URL (e.g., https://keep.example.com)
#   KARAKEEP_API_KEY - Your Karakeep API key

set -e

URL="$1"
NOTE="${2:-}"

if [ -z "$URL" ]; then
  echo "Usage: $0 <url> [note]" >&2
  exit 1
fi

if [ -z "$KARAKEEP_URL" ]; then
  echo "Error: KARAKEEP_URL environment variable not set" >&2
  echo "Set it to your Karakeep instance URL (e.g., https://keep.example.com)" >&2
  exit 1
fi

if [ -z "$KARAKEEP_API_KEY" ]; then
  echo "Error: KARAKEEP_API_KEY environment variable not set" >&2
  echo "Get your API key from Karakeep → Settings → API Keys" >&2
  exit 1
fi

# Build JSON body
if [ -n "$NOTE" ]; then
  BODY=$(jq -n --arg url "$URL" --arg note "$NOTE" '{"type": "link", "url": $url, "note": $note}')
else
  BODY=$(jq -n --arg url "$URL" '{"type": "link", "url": $url}')
fi

# Make API request
RESPONSE=$(curl -s -X POST "${KARAKEEP_URL}/api/v1/bookmarks" \
  -H "Authorization: Bearer ${KARAKEEP_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$BODY")

# Check for errors
if echo "$RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
  ID=$(echo "$RESPONSE" | jq -r '.id')
  ALREADY_EXISTS=$(echo "$RESPONSE" | jq -r '.alreadyExists')
  
  if [ "$ALREADY_EXISTS" = "true" ]; then
    echo "Bookmark already exists (id: $ID)"
  else
    echo "Saved bookmark: $URL (id: $ID)"
  fi
else
  echo "Error saving bookmark:" >&2
  echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE" >&2
  exit 1
fi
