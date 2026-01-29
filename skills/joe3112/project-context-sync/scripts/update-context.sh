#!/bin/bash
# project-context-sync: Update PROJECT_STATE.md with current git state
# Usage: update-context.sh [repo_path]

set -e

# Determine repo root
if [ -n "$1" ]; then
    REPO_ROOT="$1"
else
    REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
        echo "❌ Not in a git repository and no path provided"
        exit 1
    }
fi

cd "$REPO_ROOT"

CONFIG_FILE="$REPO_ROOT/.project-context.yml"
STATE_FILE="$REPO_ROOT/PROJECT_STATE.md"

# ─────────────────────────────────────────────────────────────────────────────
# Parse config (simple bash parsing, falls back to defaults)
# ─────────────────────────────────────────────────────────────────────────────

AI_SUMMARY="true"
RECENT_COMMITS=5
INCLUDE_DIFF_STATS="true"

if [ -f "$CONFIG_FILE" ]; then
    # Very basic YAML parsing - just grep for values
    if grep -q "ai_summary: false" "$CONFIG_FILE"; then
        AI_SUMMARY="false"
    fi
    
    RC=$(grep "recent_commits:" "$CONFIG_FILE" 2>/dev/null | awk '{print $2}' | tr -d '[:space:]')
    if [ -n "$RC" ]; then
        RECENT_COMMITS="$RC"
    fi
    
    if grep -q "include_diff_stats: false" "$CONFIG_FILE"; then
        INCLUDE_DIFF_STATS="false"
    fi
fi

# ─────────────────────────────────────────────────────────────────────────────
# Gather git information
# ─────────────────────────────────────────────────────────────────────────────

# Last commit
LAST_HASH=$(git log -1 --format="%h" 2>/dev/null || echo "none")
LAST_MSG=$(git log -1 --format="%s" 2>/dev/null || echo "No commits")
LAST_DATE=$(git log -1 --format="%ci" 2>/dev/null || echo "")
LAST_AUTHOR=$(git log -1 --format="%an" 2>/dev/null || echo "")
BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")

# Files changed in last commit
if [ "$LAST_HASH" != "none" ]; then
    # For first commit, diff-tree needs special handling
    PARENT_COUNT=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    if [ "$PARENT_COUNT" = "1" ]; then
        # First commit: list all files
        FILES_LIST=$(git ls-tree --name-only -r HEAD 2>/dev/null | head -10)
        FILES_CHANGED=$(git ls-tree --name-only -r HEAD 2>/dev/null | wc -l | tr -d ' ')
    else
        FILES_LIST=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null | head -10)
        FILES_CHANGED=$(git diff-tree --no-commit-id --name-only -r HEAD 2>/dev/null | wc -l | tr -d ' ')
    fi
else
    FILES_CHANGED=0
    FILES_LIST=""
fi

# Recent commits
RECENT=$(git log -"$RECENT_COMMITS" --format="- %h: %s" 2>/dev/null || echo "No commits yet")

# Diff stats (optional)
if [ "$INCLUDE_DIFF_STATS" = "true" ] && [ "$LAST_HASH" != "none" ]; then
    DIFF_STAT=$(git diff --stat HEAD~1 HEAD 2>/dev/null | tail -1 || echo "")
else
    DIFF_STAT=""
fi

NOW=$(date "+%Y-%m-%d %H:%M:%S")

# ─────────────────────────────────────────────────────────────────────────────
# Generate output (raw mode)
# ─────────────────────────────────────────────────────────────────────────────

generate_raw_output() {
    cat << EOF
# Project State

*Auto-updated by [project-context-sync](https://github.com/clawdbot/skills/project-context-sync)*  
*Last updated: $NOW*

---

## Last Commit

- **Hash:** $LAST_HASH
- **Message:** $LAST_MSG
- **Branch:** $BRANCH
- **Author:** $LAST_AUTHOR
- **When:** $LAST_DATE
- **Files changed:** $FILES_CHANGED
EOF

    if [ -n "$DIFF_STAT" ]; then
        echo ""
        echo "**Stats:** $DIFF_STAT"
    fi

    if [ -n "$FILES_LIST" ]; then
        echo ""
        echo "**Changed files:**"
        echo "\`\`\`"
        echo "$FILES_LIST"
        echo "\`\`\`"
    fi

    cat << EOF

## Recent Changes

$RECENT

## Current Focus

*Raw mode — set \`ai_summary: true\` and ensure CLAWDBOT_TOKEN is set for AI summaries.*

## Suggested Next Steps

*Run with AI mode for intelligent suggestions.*
EOF
}

# ─────────────────────────────────────────────────────────────────────────────
# Generate output (AI mode) - calls gateway API for smart summaries
# ─────────────────────────────────────────────────────────────────────────────

generate_ai_output() {
    # Build context for AI
    PROMPT="You are updating a PROJECT_STATE.md file for an agent workspace. Be concise and practical.

REPO: $(basename "$REPO_ROOT")
BRANCH: $BRANCH

LAST COMMIT:
- Hash: $LAST_HASH
- Message: $LAST_MSG
- Author: $LAST_AUTHOR  
- Date: $LAST_DATE
- Files: $FILES_CHANGED changed

Changed files:
$FILES_LIST

RECENT COMMITS:
$RECENT

${DIFF_STAT:+STATS: $DIFF_STAT}

Generate PROJECT_STATE.md with EXACTLY this structure:

# Project State
*Auto-updated: $NOW*

## Last Commit
(format the commit info cleanly)

## Recent Changes  
(the commit list)

## Current Focus
(2-3 sentences: what's being actively worked on, inferred from commits)

## Suggested Next Steps
(2-3 bullet points: logical next actions based on the work pattern)

Output ONLY the markdown. No preamble, no explanation."

    # Read gateway config from clawdbot config file
    CLAWDBOT_CONFIG="$HOME/.clawdbot/clawdbot.json"
    
    if [ -f "$CLAWDBOT_CONFIG" ] && command -v jq &> /dev/null; then
        CONFIG_PORT=$(jq -r '.gateway.port // empty' "$CLAWDBOT_CONFIG" 2>/dev/null)
        CONFIG_TOKEN=$(jq -r '.gateway.auth.token // empty' "$CLAWDBOT_CONFIG" 2>/dev/null)
    fi
    
    # Use config values or fall back to env/defaults
    GATEWAY_PORT="${CONFIG_PORT:-${CLAWDBOT_GATEWAY_PORT:-19000}}"
    GATEWAY_TOKEN="${CONFIG_TOKEN:-${CLAWDBOT_TOKEN:-}}"
    GATEWAY_URL="http://localhost:$GATEWAY_PORT"
    
    if [ -n "$GATEWAY_TOKEN" ]; then
        # Escape the prompt for JSON
        ESCAPED_PROMPT=$(echo "$PROMPT" | jq -Rs .)
        
        # Call gateway's OpenAI-compatible endpoint
        RESULT=$(curl -s -X POST "$GATEWAY_URL/v1/chat/completions" \
            -H "Authorization: Bearer $GATEWAY_TOKEN" \
            -H "Content-Type: application/json" \
            -H "x-clawdbot-agent-id: main" \
            -d "{\"model\": \"clawdbot\", \"messages\": [{\"role\": \"user\", \"content\": $ESCAPED_PROMPT}]}" \
            --max-time 60 2>/dev/null | jq -r '.choices[0].message.content // empty' 2>/dev/null) || RESULT=""
        
        if [ -n "$RESULT" ] && [ "$RESULT" != "null" ]; then
            echo "$RESULT"
            return
        fi
    fi
    
    # Fallback to raw if gateway not available
    generate_raw_output
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

if [ "$AI_SUMMARY" = "true" ]; then
    generate_ai_output > "$STATE_FILE"
else
    generate_raw_output > "$STATE_FILE"
fi

echo "✅ Updated: $STATE_FILE"
