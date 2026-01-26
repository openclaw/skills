#!/bin/bash
# Open a specific LinkedIn conversation using Peekaboo
# Usage: ./open_conversation.sh "person_name"

set -e

PERSON_NAME="$1"

if [ -z "$PERSON_NAME" ]; then
    echo "Usage: ./open_conversation.sh \"person_name\""
    exit 1
fi

echo "📖 Opening conversation with: $PERSON_NAME"

# Ensure Chrome is focused
peekaboo app launch "Google Chrome"
sleep 0.5

# Navigate to messaging with search
SEARCH_URL="https://www.linkedin.com/messaging/?searchTerm=$(echo "$PERSON_NAME" | sed 's/ /%20/g')"
peekaboo menu click --app "Google Chrome" --item "New Tab" 2>/dev/null || true
sleep 0.5
peekaboo type "$SEARCH_URL" --app "Google Chrome"
peekaboo press return --app "Google Chrome"
sleep 3

# Capture the conversation
OUTPUT_PATH="/tmp/linkedin-conversation-$(date +%s).png"
peekaboo see \
    --app "Google Chrome" \
    --annotate \
    --path "$OUTPUT_PATH"

echo "✅ Conversation captured: $OUTPUT_PATH"
echo "$OUTPUT_PATH"
