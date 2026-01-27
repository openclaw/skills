#!/bin/bash
# Check an IP's abuse score on AbuseIPDB
# Usage: check-ip.sh <ip>

set -euo pipefail

IP="${1:?Usage: check-ip.sh <ip>}"
API_KEY="${ABUSEIPDB_KEY:-$(pass show abuseipdb/api-key 2>/dev/null || echo "")}"

if [ -z "$API_KEY" ]; then
  echo "ERROR: No AbuseIPDB API key found."
  exit 1
fi

RESPONSE=$(curl -sG "https://api.abuseipdb.com/api/v2/check" \
  -H "Key: $API_KEY" \
  -H "Accept: application/json" \
  --data-urlencode "ipAddress=$IP" \
  -d "maxAgeInDays=90")

echo "$RESPONSE" | jq '{
  ip: .data.ipAddress,
  score: .data.abuseConfidenceScore,
  country: .data.countryCode,
  isp: .data.isp,
  domain: .data.domain,
  totalReports: .data.totalReports,
  lastReported: .data.lastReportedAt,
  isWhitelisted: .data.isWhitelisted
}'
