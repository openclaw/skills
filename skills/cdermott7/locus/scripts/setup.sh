#!/usr/bin/env bash
# Locus MCP Setup — configures mcporter with your Locus API key
set -euo pipefail

DEFAULT_URL="https://mcp.paywithlocus.com/mcp"

echo "📍 Locus Payment Setup"
echo "======================"
echo ""

# Check mcporter
if ! command -v mcporter &>/dev/null; then
  echo "mcporter is required but not installed."
  read -rp "Install mcporter now? (Y/n): " install_mcporter
  if [[ "$install_mcporter" =~ ^[Nn]$ ]]; then
    echo "Cannot continue without mcporter. Install with: npm i -g mcporter"
    exit 1
  fi
  echo "Installing mcporter..."
  npm i -g mcporter
  echo ""
fi

# Check if already configured
if mcporter config get locus &>/dev/null 2>&1; then
  echo "⚠️  Locus is already configured in mcporter."
  echo ""
  mcporter config get locus 2>/dev/null
  echo ""
  read -rp "Reconfigure with a new API key? (y/N): " reconfigure
  if [[ ! "$reconfigure" =~ ^[Yy]$ ]]; then
    echo "Keeping existing config. Run 'mcporter list locus' to verify."
    exit 0
  fi
  mcporter config remove locus 2>/dev/null || true
  echo ""
fi

# Get API key
echo "You'll need a Locus API key to connect your wallet."
echo ""
echo "  👉 Get your key at: https://app.paywithlocus.com"
echo ""
echo "Each key is tied to your wallet and permission group."
echo ""
read -rp "Paste your API key (locus_...): " api_key

if [[ -z "$api_key" ]]; then
  echo ""
  echo "❌ No API key provided. Get one at https://app.paywithlocus.com"
  exit 1
fi

if [[ ! "$api_key" =~ ^locus_ ]]; then
  echo ""
  echo "⚠️  That doesn't look like a Locus API key (should start with 'locus_')."
  read -rp "Use it anyway? (y/N): " use_anyway
  if [[ ! "$use_anyway" =~ ^[Yy]$ ]]; then
    echo "Aborted. Get your key at https://app.paywithlocus.com"
    exit 1
  fi
fi

# Configure
echo ""
echo "Configuring mcporter..."
mcporter config add locus \
  --url "$DEFAULT_URL" \
  --header "Authorization=Bearer $api_key" \
  --scope home

echo ""
echo "✅ Locus configured! Testing connection..."
echo ""

# Test and show available tools
if mcporter list locus 2>/dev/null; then
  echo ""
  echo "🎉 Setup complete! Your agent can now use Locus payment tools."
  echo ""
  echo "Next steps:"
  echo "  • Your ClawdBot agent will automatically discover Locus tools"
  echo "  • Try asking your agent to check your wallet balance"
  echo "  • Or run: mcporter call locus.list_tokens"
else
  echo ""
  echo "❌ Connection failed. Possible issues:"
  echo "  • Invalid or expired API key"
  echo "  • Network connectivity"
  echo ""
  echo "Get a new key at https://app.paywithlocus.com"
  echo "Then re-run: bash skills/locus/scripts/setup.sh"
fi
