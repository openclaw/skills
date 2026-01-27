#!/bin/bash
# Report all currently banned IPs to AbuseIPDB
# Usage: report-banned.sh [jail_name]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
JAIL="${1:-sshd}"
LOG="/var/log/abuseipdb-reports.log"

# Get banned IPs
BANNED=$(sudo fail2ban-client status "$JAIL" | grep "Banned IP list" | sed 's/.*Banned IP list:\s*//')

if [ -z "$BANNED" ]; then
  echo "No banned IPs in jail: $JAIL"
  exit 0
fi

# Read already-reported IPs from log
REPORTED_IPS=""
if [ -f "$LOG" ]; then
  REPORTED_IPS=$(grep "REPORTED" "$LOG" | awk '{print $4}' | sort -u)
fi

COUNT=0
SKIPPED=0

for IP in $BANNED; do
  # Skip already reported (within last 15 min to avoid duplicates)
  if echo "$REPORTED_IPS" | grep -q "^${IP}$"; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  echo "Reporting: $IP"
  bash "$SCRIPT_DIR/report-single.sh" "$IP" "SSH brute-force (fail2ban auto-ban on $JAIL jail)"
  COUNT=$((COUNT + 1))

  # Rate limit: small delay between reports
  sleep 1
done

echo ""
echo "Done! Reported: $COUNT | Skipped (already reported): $SKIPPED"
