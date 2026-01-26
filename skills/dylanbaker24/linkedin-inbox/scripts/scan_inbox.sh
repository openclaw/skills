#!/bin/bash
# LinkedIn Inbox Scanner using Peekaboo
# Usage: ./scan_inbox.sh [output_dir]

set -e

OUTPUT_DIR="${1:-/tmp/linkedin-inbox}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCREENSHOT_PATH="$OUTPUT_DIR/inbox_$TIMESTAMP.png"

mkdir -p "$OUTPUT_DIR"

echo "📨 Scanning LinkedIn inbox..."

# Ensure Chrome is running
if ! pgrep -x "Google Chrome" > /dev/null; then
    echo "Starting Chrome..."
    peekaboo app launch "Google Chrome"
    sleep 2
fi

# Navigate to LinkedIn messaging
echo "Navigating to LinkedIn messaging..."
peekaboo menu click --app "Google Chrome" --item "New Tab" 2>/dev/null || true
sleep 1

# Type URL and navigate
peekaboo type "https://www.linkedin.com/messaging/" --app "Google Chrome"
peekaboo press return --app "Google Chrome"
sleep 3

# Wait for page load (check for messaging UI)
echo "Waiting for page load..."
sleep 2

# Capture annotated screenshot
echo "Capturing inbox state..."
peekaboo see \
    --app "Google Chrome" \
    --annotate \
    --path "$SCREENSHOT_PATH" \
    --json > "$OUTPUT_DIR/inbox_$TIMESTAMP.json" 2>/dev/null || \
peekaboo image \
    --app "Google Chrome" \
    --path "$SCREENSHOT_PATH"

echo "✅ Inbox captured: $SCREENSHOT_PATH"
echo "📋 Analysis JSON: $OUTPUT_DIR/inbox_$TIMESTAMP.json"

# Output path for agent consumption
echo "$SCREENSHOT_PATH"
