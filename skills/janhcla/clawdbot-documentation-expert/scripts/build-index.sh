#!/bin/bash
# Build a full-text searchable index of all documentation
# Requires: qmd (for vector/BM25 search)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INDEX_DIR="${HOME}/.cache/clawddocs/index"
DOCS_DIR="${INDEX_DIR}/docs"

mkdir -p "$DOCS_DIR"

fetch_all() {
    echo "📥 Fetching all documentation..."
    
    local urls=$("$SCRIPT_DIR/cache.sh" urls)
    local total=$(echo "$urls" | wc -l | tr -d ' ')
    local count=0
    
    echo "$urls" | while read -r url; do
        count=$((count + 1))
        local path="${url#https://docs.clawd.bot/}"
        local filename="${path//\//_}.md"
        
        # Skip if recently fetched
        if [ -f "$DOCS_DIR/$filename" ]; then
            if [[ "$OSTYPE" == "darwin"* ]]; then
                age=$(( $(date +%s) - $(stat -f %m "$DOCS_DIR/$filename") ))
            else
                age=$(( $(date +%s) - $(stat -c %Y "$DOCS_DIR/$filename") ))
            fi
            if [ "$age" -lt 86400 ]; then  # 24 hours
                continue
            fi
        fi
        
        echo "[$count/$total] Fetching: $path"
        
        # Fetch content
        content=$(curl -s "$url" | \
            sed -n '/<article/,/<\/article>/p' | \
            sed 's/<[^>]*>//g' | \
            sed 's/&nbsp;/ /g; s/&amp;/\&/g; s/&lt;/</g; s/&gt;/>/g; s/&quot;/"/g' | \
            sed '/^[[:space:]]*$/d' | \
            head -1000)
        
        if [ -n "$content" ]; then
            echo "# $path" > "$DOCS_DIR/$filename"
            echo "# Source: $url" >> "$DOCS_DIR/$filename"
            echo "" >> "$DOCS_DIR/$filename"
            echo "$content" >> "$DOCS_DIR/$filename"
        fi
        
        # Rate limit
        sleep 0.5
    done
    
    echo ""
    echo "✅ Fetched docs to: $DOCS_DIR"
    echo "Total files: $(ls -1 "$DOCS_DIR" | wc -l | tr -d ' ')"
}

build_qmd_index() {
    if ! command -v qmd &> /dev/null; then
        echo "qmd not found. Install with: cargo install qmd"
        echo ""
        echo "Docs are still available in: $DOCS_DIR"
        echo "You can search with: grep -r 'query' $DOCS_DIR"
        exit 1
    fi
    
    echo "🔨 Building qmd index..."
    qmd index "$DOCS_DIR"
    echo "✅ Index built. Search with: qmd query 'your question'"
}

search() {
    local query="$1"
    
    if [ -z "$query" ]; then
        echo "Usage: build-index.sh search <query>"
        exit 1
    fi
    
    if command -v qmd &> /dev/null; then
        cd "$DOCS_DIR" && qmd query "$query"
    else
        echo "Falling back to grep search..."
        grep -ril "$query" "$DOCS_DIR" | head -20 | while read -r file; do
            echo "📄 $(basename "$file" .md | tr '_' '/')"
            grep -i "$query" "$file" | head -2 | sed 's/^/   /'
            echo ""
        done
    fi
}

status() {
    echo "📊 Index Status:"
    echo "  Docs dir: $DOCS_DIR"
    if [ -d "$DOCS_DIR" ]; then
        echo "  Files: $(ls -1 "$DOCS_DIR" 2>/dev/null | wc -l | tr -d ' ')"
        echo "  Size: $(du -sh "$DOCS_DIR" 2>/dev/null | cut -f1)"
    else
        echo "  (not initialized - run 'build-index.sh fetch')"
    fi
    
    if command -v qmd &> /dev/null; then
        echo "  qmd: available ✓"
    else
        echo "  qmd: not installed (grep fallback available)"
    fi
}

# CLI
case "${1:-}" in
    fetch) fetch_all ;;
    build) build_qmd_index ;;
    search) search "$2" ;;
    status) status ;;
    all) fetch_all && build_qmd_index ;;
    *)
        echo "Usage: build-index.sh <command>"
        echo ""
        echo "Commands:"
        echo "  fetch    Download all docs"
        echo "  build    Build qmd search index"
        echo "  all      Fetch + build"
        echo "  search   Search the index"
        echo "  status   Show index status"
        ;;
esac
