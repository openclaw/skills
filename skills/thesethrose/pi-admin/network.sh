#!/bin/bash
# Network information

echo "🌐 Network Information"
echo "======================"
echo ""

# Hostname
echo "Hostname: $(hostname)"
echo "FQDN: $(hostname -f 2>/dev/null || echo "N/A")"
echo ""

# IP Addresses
echo "IP Addresses:"
echo "-------------"
hostname -I 2>/dev/null | tr ' ' '\n' | while read ip; do
  [ -n "$ip" ] && echo "  - $ip"
done
echo ""

# Network Interfaces
echo "Network Interfaces:"
echo "-------------------"
for iface in /sys/class/net/*; do
  name=$(basename "$iface")
  if [ -f "$iface/operstate" ]; then
    state=$(cat "$iface/operstate")
    mac=$(cat "$iface/address" 2>/dev/null)
    ip=$(ip -4 addr show "$name" 2>/dev/null | grep -oP 'inet \K[0-9.]+' | head -1)
    echo "  $name: $state"
    [ -n "$ip" ] && echo "    IP: $ip"
    [ -n "$mac" ] && echo "    MAC: $mac"
  fi
done
echo ""

# DNS
echo "DNS Servers:"
echo "------------"
cat /etc/resolv.conf 2>/dev/null | grep nameserver | while read line; do
  echo "  $line"
done
echo ""

# Gateway
echo "Default Gateway:"
echo "----------------"
ip route | grep default | awk '{print "  via " $3 " dev " $5}'