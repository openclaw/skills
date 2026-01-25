#!/bin/bash
# Sync Voicenotes to markdown files
# Usage: ./sync-to-markdown.sh [--output-dir DIR]
# Requires: VOICENOTES_TOKEN environment variable, jq

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${VOICENOTES_OUTPUT_DIR:-./voicenotes}"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --output-dir) OUTPUT_DIR="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

if [ -z "$VOICENOTES_TOKEN" ]; then
  echo "Error: VOICENOTES_TOKEN environment variable not set" >&2
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Fetching voice notes..."
NOTES=$("$SCRIPT_DIR/fetch-notes.sh")

# Check for errors
if echo "$NOTES" | jq -e '.error' > /dev/null 2>&1; then
  echo "API Error: $(echo "$NOTES" | jq -r '.message // .error')" >&2
  exit 1
fi

# Process each note
COUNT=0
echo "$NOTES" | jq -c '.data[]' 2>/dev/null | while read -r note; do
  ID=$(echo "$note" | jq -r '.recording_id')
  TITLE=$(echo "$note" | jq -r '.title // "Untitled"' | tr -cd '[:alnum:] _-')
  CREATED=$(echo "$note" | jq -r '.created_at')
  DATE=$(echo "$CREATED" | cut -d'T' -f1)
  TRANSCRIPT=$(echo "$note" | jq -r '.transcript // ""')
  TAGS=$(echo "$note" | jq -r '.tags[]?.name' 2>/dev/null | tr '\n' ', ' | sed 's/, $//')
  
  # Get AI creations (summaries, etc)
  CREATIONS=$(echo "$note" | jq -r '.creations[]? | "## \(.type)\n\(.markdown_content // (.content.data | join("\n")))"' 2>/dev/null)
  
  # Build filename
  FILENAME="${DATE}-${TITLE:-$ID}.md"
  FILENAME=$(echo "$FILENAME" | tr ' ' '-' | tr -cd '[:alnum:]-_.')
  FILEPATH="${OUTPUT_DIR}/${FILENAME}"
  
  # Write markdown
  cat > "$FILEPATH" << EOF
---
voicenotes_id: ${ID}
created: ${CREATED}
tags: [${TAGS}]
---

# ${TITLE:-Untitled}

## Transcript

${TRANSCRIPT}

${CREATIONS}
EOF

  COUNT=$((COUNT + 1))
  echo "Synced: $FILENAME"
done

echo "Done! Synced notes to $OUTPUT_DIR"
