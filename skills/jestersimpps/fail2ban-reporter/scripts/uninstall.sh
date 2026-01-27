#!/bin/bash
# Remove fail2ban auto-reporting action
# Usage: sudo bash uninstall.sh

set -euo pipefail

# Remove action file
rm -f /etc/fail2ban/action.d/abuseipdb.conf

# Remove action from jail config
if [ -f /etc/fail2ban/jail.local ]; then
  sed -i '/abuseipdb/d' /etc/fail2ban/jail.local
fi

# Restart fail2ban
sudo systemctl restart fail2ban

echo "✅ Auto-reporting removed."
echo "   Manual reporting still works: bash scripts/report-banned.sh"
