#!/bin/bash
# Get Voicenotes user info
# Requires: VOICENOTES_TOKEN environment variable

set -e

API_BASE="https://api.voicenotes.com/api/integrations/obsidian-sync"

if [ -z "$VOICENOTES_TOKEN" ]; then
  echo "Error: VOICENOTES_TOKEN environment variable not set" >&2
  exit 1
fi

curl -s \
  -H "Authorization: Bearer ${VOICENOTES_TOKEN}" \
  -H "X-API-KEY: ${VOICENOTES_TOKEN}" \
  -H "Accept: application/json" \
  "${API_BASE}/user/info"
