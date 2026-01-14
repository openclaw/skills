#!/bin/bash
# Hardware information

echo "🔩 Hardware Information"
echo "========================"
echo ""

# Raspberry Pi model
echo "Raspberry Pi Model:"
echo "-------------------"
if [ -f /proc/device-tree/model ]; then
  cat /proc/device-tree/model | tr -d '\0'
  echo ""
elif command -v vcgencmd &> /dev/null; then
  vcgencmd version | head -1
  echo ""
else
  echo "  Unable to detect Pi model"
fi

# CPU info
echo ""
echo "CPU Details:"
echo "------------"
CPU_MODEL=$(grep "model name" /proc/cpuinfo | head -1 | cut -d':' -f2- | xargs)
[ -n "$CPU_MODEL" ] && echo "  Model: $CPU_MODEL"

CORES=$(nproc 2>/dev/null)
echo "  Cores: $CORES"

THREADS=$(grep -c "^processor" /proc/cpuinfo)
echo "  Threads: $THREADS"

FREQ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null | awk '{printf "%.0f MHz\n", $1/1000}')
[ -n "$FREQ" ] && echo "  Current Frequency: $FREQ"

MAX_FREQ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq 2>/dev/null | awk '{printf "%.0f MHz\n", $1/1000}')
[ -n "$MAX_FREQ" ] && echo "  Max Frequency: $MAX_FREQ"
echo ""

# Memory
echo "System Memory:"
echo "--------------"
TOTAL_MEM=$(grep MemTotal /proc/meminfo | awk '{printf "%.0f MB\n", $2/1024}')
echo "  Total: $TOTAL_MEM"

# GPU Memory
if command -v vcgencmd &> /dev/null; then
  GPU_MEM=$(vcgencmd get_config total_mem 2>/dev/null | grep -oP 'total_mem=\K[0-9]+')
  [ -n "$GPU_MEM" ] && echo "  GPU Memory: ${GPU_MEM}MB"
fi
echo ""

# Operating System
echo "Operating System:"
echo "-----------------"
if [ -f /etc/os-release ]; then
  . /etc/os-release
  echo "  Name: $PRETTY_NAME"
  echo "  Version: $VERSION_ID"
else
  echo "  Unable to detect OS"
fi

KERNEL=$(uname -r)
echo "  Kernel: $KERNEL"

ARCH=$(uname -m)
echo "  Architecture: $ARCH"
echo ""

# Uptime
echo "System Uptime:"
echo "--------------"
uptime -p 2>/dev/null || uptime | awk '{print "Up for: " $3, $4}'
echo ""

# USB devices
echo "USB Devices:"
echo "------------"
lsusb 2>/dev/null | head -5 | while read line; do
  echo "  $line"
done || echo "  None detected"