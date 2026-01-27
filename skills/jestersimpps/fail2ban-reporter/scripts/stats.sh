#!/bin/bash
# Show fail2ban + AbuseIPDB reporting stats
# Usage: stats.sh [jail_name]

JAIL="${1:-sshd}"
LOG="/var/log/abuseipdb-reports.log"

echo "═══════════════════════════════════════"
echo "  fail2ban Reporter Stats"
echo "═══════════════════════════════════════"
echo ""

# fail2ban stats
echo "📊 fail2ban ($JAIL jail):"
STATUS=$(sudo fail2ban-client status "$JAIL" 2>/dev/null)
if [ $? -eq 0 ]; then
  CURRENTLY_BANNED=$(echo "$STATUS" | grep "Currently banned" | awk '{print $NF}')
  TOTAL_BANNED=$(echo "$STATUS" | grep "Total banned" | awk '{print $NF}')
  CURRENTLY_FAILED=$(echo "$STATUS" | grep "Currently failed" | awk '{print $NF}')
  TOTAL_FAILED=$(echo "$STATUS" | grep "Total failed" | awk '{print $NF}')
  BANNED_LIST=$(echo "$STATUS" | grep "Banned IP list" | sed 's/.*Banned IP list:\s*//')

  echo "  Currently banned: $CURRENTLY_BANNED"
  echo "  Total banned:     $TOTAL_BANNED"
  echo "  Failed attempts:  $TOTAL_FAILED (current: $CURRENTLY_FAILED)"
  echo ""
  echo "  Banned IPs: $BANNED_LIST"
else
  echo "  ⚠️ fail2ban not running or jail not found"
fi

echo ""

# AbuseIPDB reporting stats
echo "📡 AbuseIPDB Reports:"
if [ -f "$LOG" ]; then
  REPORTED=$(grep -c "REPORTED" "$LOG" 2>/dev/null || echo 0)
  FAILED=$(grep -c "FAILED" "$LOG" 2>/dev/null || echo 0)
  LAST=$(tail -1 "$LOG")
  echo "  Total reported: $REPORTED"
  echo "  Failed reports: $FAILED"
  echo "  Last entry:     $LAST"
else
  echo "  No reports yet. Run report-banned.sh to start."
fi

echo ""
echo "═══════════════════════════════════════"
