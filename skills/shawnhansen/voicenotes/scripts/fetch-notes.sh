#!/bin/bash
# Fetch voice notes from Voicenotes.com API
# Usage: ./fetch-notes.sh [--since TIMESTAMP]
# Requires: VOICENOTES_TOKEN environment variable

set -e

API_BASE="https://api.voicenotes.com/api/integrations/obsidian-sync"
SINCE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --since) SINCE="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [ -z "$VOICENOTES_TOKEN" ]; then
  echo "Error: VOICENOTES_TOKEN environment variable not set" >&2
  echo "Get your token from: https://voicenotes.com/app?obsidian=true#settings" >&2
  exit 1
fi

# Build request body
if [ -n "$SINCE" ]; then
  BODY='{"obsidian_deleted_recording_ids": [], "last_synced_note_updated_at": "'"$SINCE"'"}'
else
  BODY='{"obsidian_deleted_recording_ids": []}'
fi

# Fetch notes (POST method)
curl -s \
  -X POST \
  -H "Authorization: Bearer ${VOICENOTES_TOKEN}" \
  -H "X-API-KEY: ${VOICENOTES_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "$BODY" \
  "${API_BASE}/recordings"
