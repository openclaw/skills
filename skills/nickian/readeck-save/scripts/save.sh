#!/bin/bash
# Save a URL to Readeck for later reading
# Usage: save.sh <url>
#
# Requires environment variables:
#   READECK_URL - Your Readeck instance URL (e.g., https://read.example.com)
#   READECK_API_TOKEN - Your Readeck API token

set -e

URL="$1"

if [ -z "$URL" ]; then
  echo "Usage: $0 <url>" >&2
  exit 1
fi

if [ -z "$READECK_URL" ]; then
  echo "Error: READECK_URL environment variable not set" >&2
  echo "Set it to your Readeck instance URL (e.g., https://read.example.com)" >&2
  exit 1
fi

if [ -z "$READECK_API_TOKEN" ]; then
  echo "Error: READECK_API_TOKEN environment variable not set" >&2
  echo "Get your token from Readeck → Settings → API tokens" >&2
  exit 1
fi

# Make API request
RESPONSE=$(curl -s -X POST "${READECK_URL}/api/bookmarks" \
  -H "Authorization: Bearer ${READECK_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"$URL\"}")

# Check response
STATUS=$(echo "$RESPONSE" | jq -r '.status' 2>/dev/null)
MESSAGE=$(echo "$RESPONSE" | jq -r '.message' 2>/dev/null)

if [ "$STATUS" = "202" ]; then
  echo "Saved to Readeck: $URL"
else
  echo "Error saving to Readeck:" >&2
  echo "$RESPONSE" >&2
  exit 1
fi
