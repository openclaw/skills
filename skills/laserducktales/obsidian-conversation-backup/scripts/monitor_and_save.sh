#!/bin/bash
# Token-free conversation monitoring and auto-save
# Runs via cron, no LLM calls unless warning needed

SESSION_DIR="/root/.clawdbot/agents/main/sessions"
VAULT_DIR="/root/ObsidianVault/Clawd Markdowns"
LAST_SAVE_FILE="/root/clawd/.last_save_line_count"
LAST_SNAPSHOT_FILE="/root/clawd/.last_snapshot_timestamp"
WARNING_SENT_FILE="/root/clawd/.token_warning_sent"

# Get most recent session file
get_latest_session() {
    ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1
}

# Estimate tokens (rough: 1 token ≈ 4 chars)
estimate_tokens() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo 0
        return
    fi
    local chars=$(wc -c < "$file")
    echo $((chars / 4))
}

# Get current line count (for detecting new messages)
get_line_count() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo 0
        return
    fi
    wc -l < "$file"
}

# Convert JSONL to readable markdown conversation (Obsidian chat format - FIXED)
jsonl_to_markdown() {
    local jsonl_file="$1"
    local start_line="${2:-1}"  # Default to line 1 if not specified
    
    # Use jq to parse JSONL properly, starting from specific line
    tail -n +$start_line "$jsonl_file" | while IFS= read -r line; do
        echo "$line" | jq -r -f /root/clawd/format_message_v2.jq.txt 2>/dev/null
    done
}

# Save conversation snapshot as readable transcript (INCREMENTAL)
save_snapshot() {
    local timestamp=$(date +"%Y-%m-%d-%H%M")
    local snapshot_file="$VAULT_DIR/$timestamp-incremental.md"
    local session_file=$(get_latest_session)
    
    if [[ ! -f "$session_file" ]]; then
        return
    fi
    
    local tokens=$(estimate_tokens "$session_file")
    local total_lines=$(wc -l < "$session_file")
    
    # Get the line number where we left off last time
    local last_saved_line=$(cat "$LAST_SNAPSHOT_FILE" 2>/dev/null || echo 0)
    local new_lines=$((total_lines - last_saved_line))
    
    # Only save if there are new messages (at least 10 new lines)
    if [[ $new_lines -lt 10 ]]; then
        return
    fi
    
    # Calculate which line to start from
    local start_line=$((last_saved_line + 1))
    
    cat > "$snapshot_file" <<EOF
# Incremental Conversation - $timestamp

**Auto-saved**: $(date '+%Y-%m-%d %H:%M %Z')
**Token estimate**: ${tokens}k/1,000,000 ($(( (tokens * 100) / 1000000 ))%)
**New messages since last save**: Lines $start_line to $total_lines
**Session file**: $(basename "$session_file")

---

EOF
    
    # Convert only NEW messages to markdown
    jsonl_to_markdown "$session_file" "$start_line" >> "$snapshot_file"
    
    # Update tracking file
    echo "$total_lines" > "$LAST_SNAPSHOT_FILE"
    
    echo "$snapshot_file"
}

# Main logic
SESSION_FILE=$(get_latest_session)

if [[ ! -f "$SESSION_FILE" ]]; then
    exit 0
fi

TOKENS=$(estimate_tokens "$SESSION_FILE")
CURRENT_LINES=$(get_line_count "$SESSION_FILE")
LAST_SAVE_LINES=$(cat "$LAST_SAVE_FILE" 2>/dev/null || echo 0)

# Auto-save incremental snapshot if new messages
SAVED_FILE=$(save_snapshot)

# Update the line count tracker (used for other purposes)
if [[ $CURRENT_LINES -gt $((LAST_SAVE_LINES + 10)) ]]; then
    echo $CURRENT_LINES > "$LAST_SAVE_FILE"
fi

# Token warnings (only when thresholds crossed)
if [[ $TOKENS -gt 900000 ]]; then
    if [[ ! -f "$WARNING_SENT_FILE" ]] || [[ $(cat "$WARNING_SENT_FILE") != "900k" ]]; then
        # Send urgent warning via Telegram
        BOT_TOKEN=$(jq -r '.telegram.token' /root/.clawdbot/clawdbot.json 2>/dev/null)
        if [[ -n "$BOT_TOKEN" && -n "$CHAT_ID" ]]; then
            curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
                -d "chat_id=${CHAT_ID}" \
                -d "text=🚨 URGENT: Context at ${TOKENS}k/1M (90%+) - Run /new NOW" > /dev/null
        fi
        echo "900k" > "$WARNING_SENT_FILE"
    fi
elif [[ $TOKENS -gt 800000 ]]; then
    if [[ ! -f "$WARNING_SENT_FILE" ]] || [[ $(cat "$WARNING_SENT_FILE") != "800k" ]]; then
        BOT_TOKEN=$(jq -r '.telegram.token' /root/.clawdbot/clawdbot.json 2>/dev/null)
        if [[ -n "$BOT_TOKEN" && -n "$CHAT_ID" ]]; then
            curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
                -d "chat_id=${CHAT_ID}" \
                -d "text=⚠️ TOKEN WARNING: Context at ${TOKENS}k/1M (80%+) - Consider /new soon" > /dev/null
        fi
        echo "800k" > "$WARNING_SENT_FILE"
    fi
else
    # Reset warning flag when back under threshold
    rm -f "$WARNING_SENT_FILE" 2>/dev/null
fi

exit 0
