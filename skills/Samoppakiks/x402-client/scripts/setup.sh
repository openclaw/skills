#!/bin/bash
# x402 Client Setup — Install deps and create wallet
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WALLET_DIR="$HOME/.x402"
WALLET_FILE="$WALLET_DIR/wallet.json"

echo "🔧 x402 Client Setup"
echo "===================="

# 1. Install npm dependencies
echo ""
echo "📦 Installing dependencies..."
cd "$SKILL_DIR"
npm install --quiet 2>&1 | tail -3
echo "✅ Dependencies installed"

# 2. Create wallet directory
mkdir -p "$WALLET_DIR"
chmod 700 "$WALLET_DIR"

# 3. Generate wallet if not exists
if [ -f "$WALLET_FILE" ]; then
  echo ""
  echo "👛 Wallet already exists at $WALLET_FILE"
  node "$SKILL_DIR/scripts/wallet-info.js"
else
  echo ""
  echo "🔑 Generating new EVM wallet..."
  node "$SKILL_DIR/scripts/wallet-create.js"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Fund your wallet with USDC on Base network"
echo "2. Use: node $SKILL_DIR/scripts/pay-request.js --url <service-url>"
echo "3. Check balance: node $SKILL_DIR/scripts/wallet-balance.js"
