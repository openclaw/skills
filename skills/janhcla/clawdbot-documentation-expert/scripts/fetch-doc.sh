#!/bin/bash
# Fetch a specific doc - provides URL for browser-based reading
# The docs are client-rendered, so we provide guidance for the agent
# Usage: fetch-doc.sh <doc-path>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

doc_path="$1"

if [ -z "$doc_path" ]; then
    echo "Usage: fetch-doc.sh <doc-path>"
    echo ""
    echo "Examples:"
    echo "  fetch-doc.sh gateway/configuration"
    echo "  fetch-doc.sh providers/discord"
    echo "  fetch-doc.sh concepts/queue"
    echo ""
    echo "This script provides the URL for browser-based reading."
    echo "The clawdbot docs require JavaScript rendering."
    echo ""
    echo "Available docs (first 20):"
    "$SCRIPT_DIR/cache.sh" urls | sed 's|https://docs.clawd.bot/||' | head -20
    echo "  ... (use 'cache.sh urls' for full list)"
    exit 1
fi

# Normalize path
doc_path="${doc_path#/}"
doc_path="${doc_path%/}"

# Remove base URL if included
doc_path="${doc_path#https://docs.clawd.bot/}"

url="https://docs.clawd.bot/${doc_path}"

# Verify URL exists in sitemap
if ! "$SCRIPT_DIR/cache.sh" urls | grep -q "$url"; then
    echo "⚠️  Warning: '$doc_path' not found in sitemap"
    echo ""
    echo "Did you mean one of these?"
    "$SCRIPT_DIR/search.sh" "${doc_path##*/}" 2>/dev/null | head -10
    echo ""
fi

echo "📄 Documentation: $doc_path"
echo "🔗 URL: $url"
echo ""
echo "To read this doc:"
echo "  1. Use browser tool: navigate to $url, then snapshot"
echo "  2. Or open directly in browser"
echo ""
echo "Quick summary request:"
echo "  pi_browser action=open, targetUrl=$url"
echo "  pi_browser action=snapshot"
