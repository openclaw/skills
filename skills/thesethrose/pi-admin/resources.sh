#!/bin/bash
# System resources (CPU, memory, temperature)

echo "💻 System Resources"
echo "===================="
echo ""

# CPU Load
echo "CPU Load:"
echo "---------"
uptime | awk -F'load average:' '{print "  " $2}'
echo ""

# CPU Usage per core
echo "CPU Cores:"
echo "----------"
grep '^cpu[0-9]' /proc/stat | while read line; do
  core=$(echo "$line" | awk '{print $1}')
  echo "  $core"
done
echo ""

# CPU Model
echo "CPU Model:"
echo "----------"
grep "model name" /proc/cpuinfo | head -1 | cut -d':' -f2- | xargs
echo ""

# Memory
echo "Memory:"
echo "-------"
free -h | awk '
/^Mem:/ {
  printf "  Total: %s\n", $2
  printf "  Used:  %s (%.1f%%)\n", $3, $3/$2*100
  printf "  Free:  %s\n", $4
  printf "  Cached: %s\n", $6
  printf "  Available: %s\n", $7
}'
echo ""

# Swap
echo "Swap:"
echo "-----"
free -h | awk '
/^Swap:/ {
  if ($2 != "0B") {
    printf "  Total: %s\n", $2
    printf "  Used:  %s (%.1f%%)\n", $3, $3/$2*100
    printf "  Free:  %s\n", $4
  } else {
    printf "  No swap configured\n"
  }
}'
echo ""

# Temperature
echo "Temperature:"
echo "------------"
if command -v vcgencmd &> /dev/null; then
  CPU_TEMP=$(vcgencmd measure_temp 2>/dev/null | cut -d= -f2 | cut -d\' -f1)
  if [ -n "$CPU_TEMP" ]; then
    echo "  CPU: $CPU_TEMP"
  fi
fi

# Check thermal zones
for zone in /sys/class/thermal/thermal_zone*; do
  if [ -f "$zone/type" ] && [ -f "$zone/temp" ]; then
    type=$(cat "$zone/type")
    temp=$(cat "$zone/temp" | awk '{printf "%.1f°C\n", $1/1000}')
    echo "  $type: $temp"
  fi
done