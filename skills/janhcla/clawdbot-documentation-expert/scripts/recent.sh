#!/bin/bash
# Show recently updated documentation
# Usage: recent.sh [days] (default: 7)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

days="${1:-7}"
cutoff_date=$(date -v-${days}d +%Y-%m-%d 2>/dev/null || date -d "$days days ago" +%Y-%m-%d)

echo "📅 Docs updated in the last $days days (since $cutoff_date):"
echo ""

# Get URLs with dates and filter
"$SCRIPT_DIR/cache.sh" urls-dated | while IFS=$'\t' read -r lastmod url; do
    if [ -n "$lastmod" ]; then
        doc_date="${lastmod:0:10}"
        if [[ "$doc_date" > "$cutoff_date" ]] || [[ "$doc_date" == "$cutoff_date" ]]; then
            short_url="${url#https://docs.clawd.bot/}"
            echo "  $doc_date  $short_url"
        fi
    fi
done | head -50

echo ""
echo "(Showing up to 50 most recent)"
