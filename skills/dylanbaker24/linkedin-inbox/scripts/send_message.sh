#!/bin/bash
# Send LinkedIn message using Peekaboo
# Usage: ./send_message.sh "conversation_name" "message_text"

set -e

CONVERSATION_NAME="$1"
MESSAGE_TEXT="$2"

if [ -z "$CONVERSATION_NAME" ] || [ -z "$MESSAGE_TEXT" ]; then
    echo "Usage: ./send_message.sh \"conversation_name\" \"message_text\""
    exit 1
fi

echo "💬 Sending message to: $CONVERSATION_NAME"

# Ensure we're on LinkedIn messaging
CURRENT_URL=$(peekaboo see --app "Google Chrome" --json 2>/dev/null | jq -r '.url // empty' || echo "")
if [[ "$CURRENT_URL" != *"linkedin.com/messaging"* ]]; then
    echo "Navigating to LinkedIn messaging..."
    peekaboo type "https://www.linkedin.com/messaging/" --app "Google Chrome"
    peekaboo press return --app "Google Chrome"
    sleep 3
fi

# Search for conversation
echo "Finding conversation..."
# Click search box (usually first text field in messaging)
peekaboo hotkey --keys "cmd,k" --app "Google Chrome"
sleep 0.5

# Type conversation name to filter
peekaboo type "$CONVERSATION_NAME" --app "Google Chrome"
sleep 1

# Press down + enter to select first result
peekaboo press down --app "Google Chrome"
peekaboo press return --app "Google Chrome"
sleep 2

# Type message
echo "Typing message..."
# Focus message input (usually at bottom of conversation)
peekaboo hotkey --keys "cmd,shift,m" --app "Google Chrome" 2>/dev/null || true
sleep 0.5

# Clear any existing text and type new message
peekaboo type "$MESSAGE_TEXT" --app "Google Chrome"

# Send with Enter
echo "Sending..."
peekaboo press return --app "Google Chrome"
sleep 1

echo "✅ Message sent to $CONVERSATION_NAME"
