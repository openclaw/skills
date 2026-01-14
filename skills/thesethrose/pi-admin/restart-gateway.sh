#!/bin/bash
# Restart the Clawdis Gateway

# Usage: ./restart-gateway.sh [--dry-run]

if [ "$1" = "--dry-run" ]; then
  echo "🔍 DRY RUN MODE - Gateway would restart but won't"
  echo "===================================================="
  echo ""
  
  echo "Would stop these processes:"
  pgrep -f "clawdis gateway" 2>/dev/null | while read pid; do
    echo "  PID $pid: $(ps -p $pid -o command=)"
  done
  
  echo ""
  echo "Would start Gateway on port 18789:"
  echo "  cd /home/srose/clawdis"
  echo "  pnpm clawdis gateway --port 18790"
  echo ""
  echo "To actually restart, run without --dry-run"
  exit 0
fi

echo "🔌 Restarting Clawdis Gateway"
echo "================================"
echo ""

# Stop running gateway processes
echo "Stopping any running gateway processes..."
pkill -f "clawdis gateway" 2>/dev/null
sleep 2

# Check if processes are still running
REMAINING=$(pgrep -f "clawdis gateway" | wc -l)
if [ "$REMAINING" -gt 0 ]; then
  echo "Force stopping remaining processes..."
  pkill -9 -f "clawdis gateway" 2>/dev/null
  sleep 1
fi

echo "✅ Gateway processes stopped"
echo ""

# Start new gateway
echo "Starting Gateway on port 18789..."
cd /home/srose/clawdis

# Start in background
pnpm clawdis gateway --port 18789 > /dev/null 2>&1 &
GATEWAY_PID=$!

# Wait for startup
echo "Waiting for Gateway to start..."
sleep 3

# Check if it's running
if ps -p $GATEWAY_PID > /dev/null 2>&1; then
  echo "✅ Gateway started successfully!"
  echo "   PID: $GATEWAY_PID"
  echo ""

  # Check if port is listening
  if ss -tuln | grep -q ":18789"; then
    echo "✅ Port 18790 is listening"
    echo "   Local:  http://127.0.0.1:18790"
    echo "   Network: http://192.168.1.163:18790"
    echo "   Tailscale: http://100.73.174.80:18790"
  else
    echo "⚠️  Port 18790 not yet listening (may still be starting)"
  fi
else
  echo "❌ Failed to start Gateway"
  echo ""
  echo "Check logs:"
  echo "  cd /home/srose/clawdis && pnpm clawdis gateway --port 18789"
  exit 1
fi

echo ""
echo "Gateway is ready!"