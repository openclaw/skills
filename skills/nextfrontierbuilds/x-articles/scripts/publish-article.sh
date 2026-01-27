#!/bin/bash
# publish-article.sh - Publish an article to X using browser automation
#
# Prerequisites:
# - agent-browser installed
# - clawd browser running on CDP port 18800
# - Logged into X on the browser
#
# Usage:
#   publish-article.sh <content.txt> [cover-image.png]

set -e

CDP_PORT="${CDP_PORT:-18800}"
CONTENT_FILE="$1"
COVER_IMAGE="$2"

if [ -z "$CONTENT_FILE" ]; then
  echo "Usage: publish-article.sh <content.txt> [cover-image.png]"
  echo ""
  echo "Environment variables:"
  echo "  CDP_PORT - Chrome DevTools port (default: 18800)"
  exit 1
fi

if [ ! -f "$CONTENT_FILE" ]; then
  echo "Error: Content file not found: $CONTENT_FILE"
  exit 1
fi

if [ -n "$COVER_IMAGE" ] && [ ! -f "$COVER_IMAGE" ]; then
  echo "Error: Cover image not found: $COVER_IMAGE"
  exit 1
fi

# Check agent-browser is available
if ! command -v agent-browser &> /dev/null; then
  echo "Error: agent-browser not found. Install with: npm install -g agent-browser"
  exit 1
fi

echo "=== X Article Publisher ==="
echo "Content: $CONTENT_FILE"
[ -n "$COVER_IMAGE" ] && echo "Cover: $COVER_IMAGE"
echo "CDP Port: $CDP_PORT"
echo ""

# Step 1: Navigate to article editor
echo "Step 1: Opening article editor..."
agent-browser --cdp $CDP_PORT navigate "https://x.com/compose/article"
sleep 2

# Step 2: Wait for editor to load
echo "Step 2: Waiting for editor..."
agent-browser --cdp $CDP_PORT snapshot > /tmp/x-article-snapshot.txt 2>&1
if ! grep -qi "contenteditable\|article\|editor" /tmp/x-article-snapshot.txt; then
  echo "Warning: Editor may not have loaded. Check browser."
fi

# Step 3: Paste content
echo "Step 3: Pasting content..."
cat "$CONTENT_FILE" | pbcopy
agent-browser --cdp $CDP_PORT click '[contenteditable="true"]' 2>/dev/null || true
sleep 0.5
agent-browser --cdp $CDP_PORT press "Meta+a"
sleep 0.2
agent-browser --cdp $CDP_PORT press "Meta+v"
sleep 1

# Step 4: Upload cover image if provided
if [ -n "$COVER_IMAGE" ]; then
  echo "Step 4: Uploading cover image..."
  agent-browser --cdp $CDP_PORT upload 'input[type="file"]' "$COVER_IMAGE" 2>/dev/null || {
    echo "Warning: Cover image upload may have failed. Try manually."
  }
  sleep 2
  
  # Try to click Apply button in media dialog
  echo "  Looking for Apply button..."
  agent-browser --cdp $CDP_PORT snapshot 2>/dev/null | grep -i "apply" || true
  # Note: Apply button ref varies, may need manual click
fi

echo ""
echo "=== Content Loaded ==="
echo ""
echo "Manual steps remaining:"
echo "  1. Review content formatting"
echo "  2. Add section headers (use editor toolbar)"
echo "  3. Insert inline images at section breaks"
echo "  4. Insert tweet embeds (Insert > Posts)"
echo "  5. Add cover image if not uploaded"
echo "  6. Preview article"
echo "  7. Click Publish"
echo ""
echo "To publish via CLI (after manual review):"
echo "  agent-browser --cdp $CDP_PORT snapshot | grep -i publish"
echo "  agent-browser --cdp $CDP_PORT click @<ref>  # Publish button"
echo ""

# Optional: Auto-publish (uncomment if you're confident)
# echo "Auto-publishing in 5 seconds... (Ctrl+C to cancel)"
# sleep 5
# agent-browser --cdp $CDP_PORT evaluate "(function() { 
#   const btns = document.querySelectorAll('button'); 
#   for (let btn of btns) { 
#     if (btn.innerText.includes('Publish')) { 
#       btn.click(); 
#       return 'clicked'; 
#     } 
#   } 
#   return 'not found'; 
# })()"
