#!/bin/bash
# Create hourly conversation snapshots for a specific day

DATE="${1:-2026-01-20}"
SESSION_FILE=$(ls -t /root/.clawdbot/agents/main/sessions/*.jsonl 2>/dev/null | head -1)
VAULT_DIR="/root/ObsidianVault/Clawd Markdowns"

if [[ ! -f "$SESSION_FILE" ]]; then
    echo "No session file found"
    exit 1
fi

# Get list of hours that have messages for this date
HOURS=$(grep '"type":"message"' "$SESSION_FILE" | jq -r "select(.timestamp | startswith(\"$DATE\")) | .timestamp | split(\"T\")[1] | split(\":\")[0]" | sort -u)

for HOUR in $HOURS; do
    OUTPUT_FILE="$VAULT_DIR/$DATE-${HOUR}00-hourly.md"
    
    echo "Creating $DATE hour $HOUR:00..."
    
    # Count messages in this hour
    MSG_COUNT=$(grep '"type":"message"' "$SESSION_FILE" | jq -r "select(.timestamp | startswith(\"${DATE}T${HOUR}:\")) | .timestamp" | wc -l)
    
    # Create file header
    cat > "$OUTPUT_FILE" <<EOF
# Conversation Hour: $DATE ${HOUR}:00

**Hour**: ${HOUR}:00 - ${HOUR}:59 UTC
**Messages**: $MSG_COUNT
**Session**: $(basename "$SESSION_FILE")

---

EOF
    
    # Extract and format messages for this hour
    grep '"type":"message"' "$SESSION_FILE" | while IFS= read -r line; do
        # Filter for this hour and format
        TIMESTAMP=$(echo "$line" | jq -r '.timestamp // ""')
        if [[ "$TIMESTAMP" == ${DATE}T${HOUR}:* ]]; then
            echo "$line" | jq -r -f /root/clawd/format_message_v2.jq.txt 2>/dev/null
        fi
    done >> "$OUTPUT_FILE"
    
    echo "  ✓ Created: $OUTPUT_FILE ($MSG_COUNT messages)"
done

echo ""
echo "Done! Created hourly snapshots for $DATE"
