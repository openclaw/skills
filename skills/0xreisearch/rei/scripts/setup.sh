#!/usr/bin/env bash
# Rei setup script
# Usage: ./setup.sh <API_KEY>

set -e

API_KEY="${1:-}"
CONFIG_FILE="${HOME}/.clawdbot/clawdbot.json"

if [[ -z "$API_KEY" ]]; then
  echo "Usage: $0 <REI_API_KEY>"
  echo ""
  read -p "Enter your Rei API key: " API_KEY
  if [[ -z "$API_KEY" ]]; then
    echo "Error: API key required"
    exit 1
  fi
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Error: Clawdbot config not found at $CONFIG_FILE"
  echo "Run 'clawdbot configure' first."
  exit 1
fi

if ! command -v jq &> /dev/null; then
  echo "Error: jq is required but not installed."
  echo "Install with: sudo dnf install jq (Fedora) or brew install jq (macOS)"
  exit 1
fi

echo "Adding Rei provider to Clawdbot config..."

# Backup config
cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"

# Create the rei provider config
REI_PROVIDER=$(cat <<EOF
{
  "baseUrl": "https://coder.reilabs.org/v1",
  "apiKey": "$API_KEY",
  "api": "openai-completions",
  "headers": {
    "User-Agent": "Clawdbot/1.0"
  },
  "models": [
    {
      "id": "rei-qwen3-coder",
      "name": "Rei Qwen3 Coder",
      "reasoning": false,
      "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 200000,
      "maxTokens": 8192
    }
  ]
}
EOF
)

# Add rei provider
jq --argjson rei "$REI_PROVIDER" '.models.providers.rei = $rei' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"

# Add rei to model allowlist so switching works
jq '.agents.defaults.models["rei/rei-qwen3-coder"] = {"alias": "rei"}' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"

echo "✅ Rei provider added to config"
echo "✅ Rei added to model allowlist"
echo ""
echo "Restarting Clawdbot gateway..."
clawdbot gateway restart

echo ""
echo "✅ Done! You can now use rei/rei-qwen3-coder"
echo ""
echo "Switch to Rei:  /model rei  OR  ./scripts/switch.sh rei"
echo "Switch back:    /model opus OR  ./scripts/switch.sh opus"
