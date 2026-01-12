#!/bin/bash
# Track documentation changes over time
# Stores snapshots and diffs

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TRACK_DIR="${HOME}/.cache/clawddocs/history"

mkdir -p "$TRACK_DIR"

# Get current snapshot
snapshot() {
    local today=$(date +%Y-%m-%d)
    local snapshot_file="${TRACK_DIR}/${today}.txt"
    
    "$SCRIPT_DIR/cache.sh" urls > "$snapshot_file"
    echo "Snapshot saved: $snapshot_file"
    echo "Total docs: $(wc -l < "$snapshot_file" | tr -d ' ')"
}

# Compare two dates
diff_dates() {
    local date1="$1"
    local date2="$2"
    
    local file1="${TRACK_DIR}/${date1}.txt"
    local file2="${TRACK_DIR}/${date2}.txt"
    
    if [ ! -f "$file1" ]; then
        echo "No snapshot for $date1"
        exit 1
    fi
    if [ ! -f "$file2" ]; then
        echo "No snapshot for $date2"
        exit 1
    fi
    
    echo "📊 Changes from $date1 to $date2:"
    echo ""
    
    # New docs
    new=$(comm -13 "$file1" "$file2")
    if [ -n "$new" ]; then
        echo "➕ Added:"
        echo "$new" | sed 's|https://docs.clawd.bot/||; s/^/  /'
        echo ""
    fi
    
    # Removed docs
    removed=$(comm -23 "$file1" "$file2")
    if [ -n "$removed" ]; then
        echo "➖ Removed:"
        echo "$removed" | sed 's|https://docs.clawd.bot/||; s/^/  /'
        echo ""
    fi
    
    if [ -z "$new" ] && [ -z "$removed" ]; then
        echo "No structural changes (same docs exist)"
    fi
}

# Show available snapshots
list() {
    echo "📁 Available snapshots:"
    ls -1 "$TRACK_DIR"/*.txt 2>/dev/null | xargs -I{} basename {} .txt | sed 's/^/  /'
    
    if [ -z "$(ls -A "$TRACK_DIR"/*.txt 2>/dev/null)" ]; then
        echo "  (none - run 'track-changes.sh snapshot' to create one)"
    fi
}

# Compare with latest snapshot
since() {
    local compare_date="$1"
    local latest=$(ls -1 "$TRACK_DIR"/*.txt 2>/dev/null | sort -r | head -1 | xargs basename 2>/dev/null | sed 's/.txt//')
    
    if [ -z "$latest" ]; then
        echo "No snapshots found. Run 'track-changes.sh snapshot' first."
        exit 1
    fi
    
    if [ -z "$compare_date" ]; then
        echo "Usage: track-changes.sh since <date>"
        echo "Available snapshots:"
        list
        exit 1
    fi
    
    diff_dates "$compare_date" "$latest"
}

# CLI
case "${1:-}" in
    snapshot) snapshot ;;
    diff) diff_dates "$2" "$3" ;;
    since) since "$2" ;;
    list) list ;;
    *)
        echo "Usage: track-changes.sh <command>"
        echo ""
        echo "Commands:"
        echo "  snapshot        Save current doc list"
        echo "  list            Show available snapshots"
        echo "  since <date>    Show changes since date"
        echo "  diff <d1> <d2>  Compare two snapshots"
        ;;
esac
