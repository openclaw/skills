#!/bin/bash
# project-context-sync: Remove hook from current repo

set -e

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "❌ Not in a git repository"
    exit 1
}

echo "🧹 Uninstalling project-context-sync from: $REPO_ROOT"

# Remove hook
HOOK_FILE="$REPO_ROOT/.git/hooks/post-commit"
if [ -f "$HOOK_FILE" ]; then
    if grep -q "project-context-sync" "$HOOK_FILE"; then
        # Check if it's entirely our hook or just appended
        if head -n 3 "$HOOK_FILE" | grep -q "project-context-sync"; then
            rm "$HOOK_FILE"
            echo "   ✓ Removed post-commit hook"
        else
            # It was appended to existing hook, remove our lines
            sed -i '' '/# project-context-sync/d' "$HOOK_FILE"
            sed -i '' '/update-context.sh/d' "$HOOK_FILE"
            echo "   ✓ Removed our lines from post-commit hook"
        fi
    else
        echo "   ⚠️  Hook exists but wasn't ours"
    fi
else
    echo "   ✓ No hook to remove"
fi

echo ""
echo "✅ Uninstalled!"
echo ""
echo "Note: .project-context.yml and PROJECT_STATE.md were left in place."
echo "Remove manually if you don't need them."
