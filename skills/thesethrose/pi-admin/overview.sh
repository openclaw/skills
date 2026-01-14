#!/bin/bash
# Quick system overview

echo "🥧 Raspberry Pi Quick Overview"
echo "================================"
echo ""
echo "Hostname: $(hostname)"
echo "Uptime: $(uptime -p)"
echo "Users logged in: $(who | wc -l)"
echo ""
echo "Quick Load: $(uptime | awk -F'load average:' '{print $2}')"
echo "Memory: $(free -h | awk '/^Mem:/ {printf "%s used / %s total (%.0f%%)\n", $3, $2, $3/$2*100}')"
echo "Disk (/): $(df -h / | awk 'NR==2 {printf "%s used / %s total (%.0f%%)\n", $3, $2, $5}')"
echo "CPU Temp: $(vcgencmd measure_temp 2>/dev/null || echo "N/A")"
echo ""
echo "Top 5 CPU processes:"
ps aux --sort=-%cpu | head -6 | awk '{printf "%-10s %6s %s\n", $1, $3, $11}' | tail -5