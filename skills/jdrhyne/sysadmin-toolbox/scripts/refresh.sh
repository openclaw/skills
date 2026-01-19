#!/bin/bash
# Refresh sysadmin-toolbox from The Book of Secret Knowledge repo
# Run periodically to keep references current

set -e

REPO_URL="https://github.com/trimstray/the-book-of-secret-knowledge.git"
TEMP_DIR="/tmp/tbsk-refresh-$$"
SKILL_DIR="${1:-$HOME/clawd-duke-leto/skills/sysadmin-toolbox}"

echo "🔄 Refreshing sysadmin-toolbox from upstream..."

# Clone fresh copy
git clone --depth 1 "$REPO_URL" "$TEMP_DIR" 2>/dev/null

cd "$TEMP_DIR"

# Extract sections
echo "📦 Extracting references..."

awk '/^#### Shell One-liners/,/^#### Shell Tricks/' README.md > "$SKILL_DIR/references/shell-oneliners.md"
awk '/^#### Shell Tricks/,/^#### Shell Functions/' README.md > "$SKILL_DIR/references/shell-tricks.md"
awk '/^#### CLI Tools/,/^#### GUI Tools/' README.md > "$SKILL_DIR/references/cli-tools.md"
awk '/^#### Web Tools/,/^#### Systems\/Services/' README.md > "$SKILL_DIR/references/web-tools.md"
awk '/^#### Hacking\/Penetration Testing/,/^#### Your daily knowledge/' README.md > "$SKILL_DIR/references/security-tools.md"

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ sysadmin-toolbox refreshed from upstream"
echo "   Shell one-liners: $(wc -l < "$SKILL_DIR/references/shell-oneliners.md") lines"
