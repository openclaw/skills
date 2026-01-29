#!/bin/bash
# check-balance.sh - Check USDC balance for x402 payments
#
# Usage:
#   ./check-balance.sh <wallet_address> [network]
#
# Networks: base (default), ethereum, arbitrum, optimism, polygon

set -e

WALLET="${1:-}"
NETWORK="${2:-base}"

if [ -z "$WALLET" ]; then
  echo "Usage: check-balance.sh <wallet_address> [network]"
  echo "Networks: base, ethereum, arbitrum, optimism, polygon"
  exit 1
fi

# USDC contract addresses
declare -A USDC_ADDRESSES=(
  ["base"]="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
  ["ethereum"]="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
  ["arbitrum"]="0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
  ["optimism"]="0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"
  ["polygon"]="0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
)

# RPC endpoints
declare -A RPC_URLS=(
  ["base"]="${BASE_RPC_URL:-https://mainnet.base.org}"
  ["ethereum"]="${ETH_RPC_URL:-https://eth.llamarpc.com}"
  ["arbitrum"]="${ARB_RPC_URL:-https://arb1.arbitrum.io/rpc}"
  ["optimism"]="${OP_RPC_URL:-https://mainnet.optimism.io}"
  ["polygon"]="${POLYGON_RPC_URL:-https://polygon-rpc.com}"
)

USDC="${USDC_ADDRESSES[$NETWORK]}"
RPC="${RPC_URLS[$NETWORK]}"

if [ -z "$USDC" ]; then
  echo "Error: Unknown network '$NETWORK'"
  exit 1
fi

# ERC20 balanceOf(address) selector: 0x70a08231
# Pad address to 32 bytes
PADDED_WALLET=$(printf '%064s' "${WALLET:2}" | tr ' ' '0')
DATA="0x70a08231000000000000000000000000${PADDED_WALLET}"

# Make eth_call
RESULT=$(curl -s -X POST "$RPC" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"eth_call\",
    \"params\": [{
      \"to\": \"$USDC\",
      \"data\": \"$DATA\"
    }, \"latest\"],
    \"id\": 1
  }" | jq -r '.result')

if [ "$RESULT" = "null" ] || [ -z "$RESULT" ]; then
  echo "Error: Failed to fetch balance"
  exit 1
fi

# Convert hex to decimal and format (USDC has 6 decimals)
BALANCE_WEI=$(printf "%d" "$RESULT" 2>/dev/null || echo "0")
BALANCE_USDC=$(echo "scale=6; $BALANCE_WEI / 1000000" | bc)

echo "Wallet: $WALLET"
echo "Network: $NETWORK"
echo "USDC Balance: $BALANCE_USDC USDC"
