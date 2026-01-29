#!/bin/bash
# project-context-sync: Install hook in current repo

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "❌ Not in a git repository"
    exit 1
}

echo "🔧 Installing project-context-sync in: $REPO_ROOT"

# 1. Install post-commit hook
HOOKS_DIR="$REPO_ROOT/.git/hooks"
HOOK_FILE="$HOOKS_DIR/post-commit"

if [ -f "$HOOK_FILE" ]; then
    # Check if it's our hook
    if grep -q "project-context-sync" "$HOOK_FILE"; then
        echo "   ✓ Hook already installed"
    else
        echo "   ⚠️  Existing post-commit hook found, appending..."
        echo "" >> "$HOOK_FILE"
        echo "# project-context-sync" >> "$HOOK_FILE"
        echo "\"$SKILL_DIR/scripts/update-context.sh\" \"$REPO_ROOT\"" >> "$HOOK_FILE"
    fi
else
    cp "$SKILL_DIR/scripts/post-commit-hook.sh" "$HOOK_FILE"
    # Replace placeholder with actual paths
    sed -i '' "s|__SKILL_DIR__|$SKILL_DIR|g" "$HOOK_FILE"
    sed -i '' "s|__REPO_ROOT__|$REPO_ROOT|g" "$HOOK_FILE"
    chmod +x "$HOOK_FILE"
    echo "   ✓ Hook installed"
fi

# 2. Create config if not exists
CONFIG_FILE="$REPO_ROOT/.project-context.yml"
if [ ! -f "$CONFIG_FILE" ]; then
    cp "$SKILL_DIR/templates/project-context.yml" "$CONFIG_FILE"
    echo "   ✓ Config created: .project-context.yml"
else
    echo "   ✓ Config exists: .project-context.yml"
fi

# 3. Create initial PROJECT_STATE.md if not exists
STATE_FILE="$REPO_ROOT/PROJECT_STATE.md"
if [ ! -f "$STATE_FILE" ]; then
    cp "$SKILL_DIR/templates/PROJECT_STATE.md" "$STATE_FILE"
    echo "   ✓ Created: PROJECT_STATE.md"
else
    echo "   ✓ Exists: PROJECT_STATE.md"
fi

# 4. Add to .gitignore if not already there
GITIGNORE="$REPO_ROOT/.gitignore"
if [ -f "$GITIGNORE" ]; then
    if ! grep -q "PROJECT_STATE.md" "$GITIGNORE"; then
        echo "" >> "$GITIGNORE"
        echo "# project-context-sync (auto-generated, local only)" >> "$GITIGNORE"
        echo "PROJECT_STATE.md" >> "$GITIGNORE"
        echo "   ✓ Added PROJECT_STATE.md to .gitignore"
    else
        echo "   ✓ Already in .gitignore"
    fi
else
    echo "# project-context-sync (auto-generated, local only)" > "$GITIGNORE"
    echo "PROJECT_STATE.md" >> "$GITIGNORE"
    echo "   ✓ Created .gitignore with PROJECT_STATE.md"
fi

echo ""
echo "✅ project-context-sync installed!"
echo ""
echo "Next steps:"
echo "  • Edit .project-context.yml to customize"
echo "  • Make a commit to trigger the first update"
echo "  • Or run: $SKILL_DIR/scripts/update-context.sh"
