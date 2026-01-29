#!/bin/bash
set -e

CONFIG_DIR="$HOME/.moltbot"
CONFIG_FILE="$CONFIG_DIR/moltbot.json"

# Ensure directories exist (volume may be empty on first run)
mkdir -p "$CONFIG_DIR/agents/default/agent"
mkdir -p "$CONFIG_DIR/skills"
mkdir -p "$HOME/clawd/skills"

# Only write config if it does NOT already exist (preserves session across restarts)
if [ ! -f "$CONFIG_FILE" ]; then
    echo "First run: writing minimal MoltBot config..."
    cat > "$CONFIG_FILE" << 'EOF'
{
  "gateway": {
    "port": 18789
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514"
      }
    }
  }
}
EOF
    echo "Config written to $CONFIG_FILE"
else
    echo "Existing config found, preserving session."
fi

# Start gateway or run custom command
MOLTBOT_SRC="$HOME/moltbot-src"

if [ "$1" = "gateway" ]; then
    echo "Starting MoltBot gateway on port 18789..."
    cd "$MOLTBOT_SRC"
    exec pnpm moltbot gateway --port 18789 --verbose --allow-unconfigured
else
    cd "$MOLTBOT_SRC"
    exec pnpm moltbot "$@"
fi
