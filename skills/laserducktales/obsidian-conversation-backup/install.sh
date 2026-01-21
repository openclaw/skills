#!/bin/bash
# Installation script for Obsidian Conversation Backup skill

echo "🦞 Obsidian Conversation Backup - Installation"
echo "=============================================="
echo ""

# Get configuration from user
read -p "Obsidian vault path [/root/ObsidianVault/Clawd Markdowns]: " VAULT_PATH
VAULT_PATH=${VAULT_PATH:-/root/ObsidianVault/Clawd Markdowns}

read -p "Session directory [/root/.clawdbot/agents/main/sessions]: " SESSION_DIR
SESSION_DIR=${SESSION_DIR:-/root/.clawdbot/agents/main/sessions}

read -p "Tracking directory [/root/clawd]: " TRACKING_DIR
TRACKING_DIR=${TRACKING_DIR:-/root/clawd}

echo ""
echo "Configuration:"
echo "  Vault: $VAULT_PATH"
echo "  Sessions: $SESSION_DIR"
echo "  Tracking: $TRACKING_DIR"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled"
    exit 1
fi

# Make scripts executable
chmod +x scripts/*.sh
# Rename .txt files back to original extensions
mv config.example.txt config.example 2>/dev/null
mv scripts/format_message_v2.jq.txt scripts/format_message_v2.jq 2>/dev/null

# Update paths in scripts
for script in scripts/*.sh; do
    sed -i "s|VAULT_DIR=\".*\"|VAULT_DIR=\"$VAULT_PATH\"|g" "$script"
    sed -i "s|/root/.clawdbot/agents/main/sessions|$SESSION_DIR|g" "$script"
    sed -i "s|/root/clawd|$TRACKING_DIR|g" "$script"
done

# Create vault directory if needed
mkdir -p "$VAULT_PATH"

# Create tracking directory if needed
mkdir -p "$TRACKING_DIR"

echo ""
echo "✓ Scripts configured and made executable"
echo ""
echo "Next steps:"
echo "1. Test: ./scripts/save_full_snapshot.sh test"
echo "2. Add to crontab for hourly backups:"
echo "   crontab -e"
echo "   # Add this line:"
echo "   0 * * * * $(pwd)/scripts/monitor_and_save.sh"
echo ""
echo "Installation complete! 🎉"
