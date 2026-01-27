#!/usr/bin/env bash
# Revert Rei setup - restores config backup
# Usage: ./revert.sh

set -e

CONFIG_FILE="${HOME}/.clawdbot/clawdbot.json"
BACKUP_FILE="${CONFIG_FILE}.bak"

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "Error: No backup found at $BACKUP_FILE"
  echo "Nothing to revert."
  exit 1
fi

echo "Restoring config from backup..."
cp "$BACKUP_FILE" "$CONFIG_FILE"

echo "Restarting Clawdbot gateway..."
clawdbot gateway restart

echo ""
echo "✅ Reverted to previous config"
