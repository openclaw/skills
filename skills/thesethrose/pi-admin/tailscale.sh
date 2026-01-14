#!/bin/bash
# Tailscale information

echo "🐉 Tailscale Information"
echo "========================="
echo ""

# Check if Tailscale is installed
if ! command -v tailscale &> /dev/null; then
  echo "Tailscale is not installed"
  exit 0
fi

# Status
echo "Status:"
echo "-------"
tailscale status 2>/dev/null || echo "  Not connected or not running"
echo ""

# Tailscale IP
echo "Tailscale IPs:"
echo "--------------"
tailscale ip 2>/dev/null | while read ip; do
  echo "  - $ip"
done
echo ""

# Peers
echo "Connected Peers:"
echo "----------------"
tailscale status 2>/dev/null | grep -E "^#|^.*:.*\." | head -20
echo ""

# Exit Node
echo "Exit Node:"
echo "----------"
EXIT_NODE=$(tailscale status 2>/dev/null | grep -o "exit node .*" | cut -d':' -f2 | xargs)
if [ -n "$EXIT_NODE" ]; then
  echo "  $EXIT_NODE"
else
  echo "  No exit node configured"
fi
echo ""

# Version
echo "Version:"
echo "--------"
tailscale version 2>/dev/null | head -1