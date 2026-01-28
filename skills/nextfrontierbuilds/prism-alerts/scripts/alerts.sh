#!/bin/bash
# PRISM Pump.fun Alerts
# Usage: ./alerts.sh <command>

PRISM_URL="${PRISM_URL:-https://strykr-prism.up.railway.app}"

case "$1" in
  bonding)
    echo "🔥 Current Pump.fun Bonding Tokens"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    curl -s "$PRISM_URL/crypto/trending/solana/bonding" | jq -r '
      .tokens[:10][] | 
      "• \(.symbol) - MC: $\(.market_cap) - \(.bonding_progress)% bonded"
    ' 2>/dev/null || echo "Error fetching data"
    ;;
    
  graduated)
    echo "🎓 Recently Graduated Tokens"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    curl -s "$PRISM_URL/crypto/trending/solana/graduated" | jq -r '
      .tokens[:10][] | 
      "• \(.symbol) - MC: $\(.market_cap) - Graduated \(.graduated_at)"
    ' 2>/dev/null || echo "Error fetching data"
    ;;
    
  watch)
    echo "👀 Watching for new Pump.fun tokens..."
    echo "Press Ctrl+C to stop"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    SEEN_FILE="/tmp/prism_seen_tokens.txt"
    touch "$SEEN_FILE"
    
    while true; do
      # Fetch current bonding tokens
      TOKENS=$(curl -s "$PRISM_URL/crypto/trending/solana/bonding" | jq -r '.tokens[].contract // empty' 2>/dev/null)
      
      for TOKEN in $TOKENS; do
        if ! grep -q "$TOKEN" "$SEEN_FILE"; then
          echo "$TOKEN" >> "$SEEN_FILE"
          
          # Get token details
          DETAILS=$(curl -s "$PRISM_URL/crypto/trending/solana/bonding" | jq -r ".tokens[] | select(.contract == \"$TOKEN\")")
          SYMBOL=$(echo "$DETAILS" | jq -r '.symbol')
          MC=$(echo "$DETAILS" | jq -r '.market_cap')
          
          echo ""
          echo "🚀 NEW TOKEN DETECTED!"
          echo "Symbol: $SYMBOL"
          echo "Contract: $TOKEN"
          echo "Market Cap: \$$MC"
          echo "Time: $(date)"
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        fi
      done
      
      sleep 30
    done
    ;;
    
  *)
    echo "PRISM Pump.fun Alerts"
    echo ""
    echo "Usage: ./alerts.sh <command>"
    echo ""
    echo "Commands:"
    echo "  bonding     - Show current bonding tokens"
    echo "  graduated   - Show recently graduated tokens"
    echo "  watch       - Watch for new tokens (polls every 30s)"
    ;;
esac
