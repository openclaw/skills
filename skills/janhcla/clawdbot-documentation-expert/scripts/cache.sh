#!/bin/bash
# Cache management for clawddocs
# Caches sitemap with 1-hour TTL

CACHE_DIR="${HOME}/.cache/clawddocs"
SITEMAP_CACHE="${CACHE_DIR}/sitemap.xml"
SITEMAP_URL="https://docs.clawd.bot/sitemap.xml"
TTL_SECONDS=3600  # 1 hour

mkdir -p "$CACHE_DIR"

# Check if cache exists and is fresh
is_cache_fresh() {
    if [ ! -f "$SITEMAP_CACHE" ]; then
        return 1
    fi
    
    local cache_age
    if [[ "$OSTYPE" == "darwin"* ]]; then
        cache_age=$(( $(date +%s) - $(stat -f %m "$SITEMAP_CACHE") ))
    else
        cache_age=$(( $(date +%s) - $(stat -c %Y "$SITEMAP_CACHE") ))
    fi
    
    [ "$cache_age" -lt "$TTL_SECONDS" ]
}

# Get sitemap (from cache or fresh)
get_sitemap() {
    if is_cache_fresh; then
        cat "$SITEMAP_CACHE"
    else
        curl -s "$SITEMAP_URL" | tee "$SITEMAP_CACHE"
    fi
}

# Extract URLs from sitemap
get_urls() {
    get_sitemap | sed -n 's/.*<loc>\([^<]*\)<\/loc>.*/\1/p' | sort
}

# Extract URLs with lastmod dates
get_urls_with_dates() {
    get_sitemap | awk '
        /<url>/ { url=""; lastmod="" }
        /<loc>/ { gsub(/.*<loc>|<\/loc>.*/, ""); url=$0 }
        /<lastmod>/ { gsub(/.*<lastmod>|<\/lastmod>.*/, ""); lastmod=$0 }
        /<\/url>/ { if(url) print lastmod "\t" url }
    ' | sort -r
}

# Force refresh
refresh() {
    rm -f "$SITEMAP_CACHE"
    get_sitemap > /dev/null
    echo "Cache refreshed"
}

# Show cache status
status() {
    if [ -f "$SITEMAP_CACHE" ]; then
        local age
        if [[ "$OSTYPE" == "darwin"* ]]; then
            age=$(( $(date +%s) - $(stat -f %m "$SITEMAP_CACHE") ))
        else
            age=$(( $(date +%s) - $(stat -c %Y "$SITEMAP_CACHE") ))
        fi
        local mins=$((age / 60))
        echo "Cache: $SITEMAP_CACHE"
        echo "Age: ${mins}m (TTL: $((TTL_SECONDS / 60))m)"
        echo "URLs: $(get_urls | wc -l | tr -d ' ')"
        if [ "$age" -lt "$TTL_SECONDS" ]; then
            echo "Status: FRESH ✓"
        else
            echo "Status: STALE (will refresh on next use)"
        fi
    else
        echo "Cache: not initialized"
    fi
}

# CLI
case "${1:-}" in
    urls) get_urls ;;
    urls-dated) get_urls_with_dates ;;
    refresh) refresh ;;
    status) status ;;
    raw) get_sitemap ;;
    *) echo "Usage: cache.sh [urls|urls-dated|refresh|status|raw]" ;;
esac
