#!/bin/bash
# Services and processes

echo "🔧 Services Information"
echo "========================"
echo ""

# Gateway service
echo "Gateway Service:"
echo "----------------"
pgrep -f "clawdis gateway" > /dev/null && echo "  ✅ Running" || echo "  ❌ Not running"
if pgrep -f "clawdis gateway" > /dev/null; then
  pids=$(pgrep -f "clawdis gateway" | tr '\n' ' ')
  echo "  PIDs: $pids"
fi
echo ""

# Systemctl services
echo "Systemd Services:"
echo "-----------------"
systemctl list-units --type=service --state=running --no-pager 2>/dev/null | grep -E "ssh|nginx|docker|pi" | head -10 | awk '{
  printf "  %-30s %s\n", $1, $4
}'
echo ""

# Docker
if command -v docker &> /dev/null; then
  echo "Docker Containers:"
  echo "------------------"
  if docker ps &> /dev/null; then
    RUNNING=$(docker ps -q | wc -l)
    TOTAL=$(docker ps -a -q | wc -l)
    echo "  Running: $RUNNING / Total: $TOTAL"
    echo ""
    docker ps --format "  table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | head -6
  else
    echo "  Docker daemon not running"
  fi
  echo ""
fi

# Port listeners
echo "Listening Ports:"
echo "----------------"
ss -tuln | grep LISTEN | awk '{
  printf "  %-10s %-6s %s\n", $1, $5, $6
}' | head -10
echo ""

# Recent errors in syslog
echo "Recent System Errors (last 10):"
echo "--------------------------------"
grep -i "error\|fail\|critical" /var/log/syslog 2>/dev/null | tail -10 | awk '{
  print "  " $0
}' || echo "  (Unable to read syslog)"