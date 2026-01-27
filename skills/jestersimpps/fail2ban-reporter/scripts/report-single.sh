#!/bin/bash
# Report a single IP to AbuseIPDB
# Usage: report-single.sh <ip> [comment]

set -euo pipefail

IP="${1:?Usage: report-single.sh <ip> [comment]}"
COMMENT="${2:-SSH brute-force attack detected by fail2ban}"
LOG="/var/log/abuseipdb-reports.log"
API_KEY="${ABUSEIPDB_KEY:-$(pass show abuseipdb/api-key 2>/dev/null || echo "")}"

if [ -z "$API_KEY" ]; then
  echo "ERROR: No AbuseIPDB API key found."
  echo "Set ABUSEIPDB_KEY or run: pass insert abuseipdb/api-key"
  exit 1
fi

# Report to AbuseIPDB
RESPONSE=$(curl -s -w "\n%{http_code}" \
  "https://api.abuseipdb.com/api/v2/report" \
  -H "Key: $API_KEY" \
  -H "Accept: application/json" \
  --data-urlencode "ip=$IP" \
  -d "categories=18,22" \
  --data-urlencode "comment=$COMMENT")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

TIMESTAMP=$(date -u '+%Y-%m-%d %H:%M:%S UTC')

if [ "$HTTP_CODE" = "200" ]; then
  SCORE=$(echo "$BODY" | jq -r '.data.abuseConfidenceScore // "unknown"')
  echo "$TIMESTAMP | REPORTED | $IP | score: $SCORE | $COMMENT" >> "$LOG"
  echo "✅ Reported $IP to AbuseIPDB (confidence score: $SCORE)"
else
  ERROR=$(echo "$BODY" | jq -r '.errors[0].detail // "unknown error"' 2>/dev/null || echo "$BODY")
  echo "$TIMESTAMP | FAILED | $IP | HTTP $HTTP_CODE | $ERROR" >> "$LOG"
  echo "❌ Failed to report $IP: $ERROR (HTTP $HTTP_CODE)"
fi
