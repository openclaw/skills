#!/bin/bash
# Search clawdbot documentation by keyword
# Usage: search.sh <query> [--full]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

query="$1"
full_mode="${2:-}"

if [ -z "$query" ]; then
    echo "Usage: search.sh <query> [--full]"
    echo ""
    echo "Examples:"
    echo "  search.sh discord        # Find docs mentioning 'discord'"
    echo "  search.sh webhook --full # Show full paths"
    exit 1
fi

# Get URLs from cache
urls=$("$SCRIPT_DIR/cache.sh" urls)

# Search (case-insensitive)
matches=$(echo "$urls" | grep -i "$query")

if [ -z "$matches" ]; then
    echo "No docs found matching '$query'"
    exit 0
fi

count=$(echo "$matches" | wc -l | tr -d ' ')
echo "📖 Found $count docs matching '$query':"
echo ""

if [ "$full_mode" = "--full" ]; then
    echo "$matches"
else
    echo "$matches" | sed 's|https://docs.clawd.bot/||' | sed 's/^/  - /'
fi
