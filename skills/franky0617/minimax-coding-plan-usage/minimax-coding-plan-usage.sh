#!/bin/bash
# Minimax Coding Plan Usage Check
# Usage: ./minimax-usage.sh
# Requires: MINIMAX_CODING_API_KEY and MINIMAX_GROUP_ID in .env

source "$(dirname "$0")/../../.env"

API_KEY="${MINIMAX_CODING_API_KEY}"
GROUP_ID="${MINIMAX_GROUP_ID}"

if [ -z "$API_KEY" ] || [ -z "$GROUP_ID" ]; then
  echo "❌ Error: MINIMAX_CODING_API_KEY and MINIMAX_GROUP_ID required in .env"
  exit 1
fi

echo "🔍 Checking Minimax Coding Plan usage..."

RESPONSE=$(curl --location "https://platform.minimax.com/v1/api/openplatform/coding_plan/remains?GroupId=${GROUP_ID}" \
  --header "accept: application/json, text/plain, */*" \
  --header "authorization: Bearer $API_KEY" \
  --header "referer: https://platform.minimax.com/user-center/payment/coding-plan" \
  --header "user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36" \
  --write-out "\nHTTP_STATUS:%{http_code}" \
  2>/dev/null)

STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

if [ "$STATUS" = "200" ]; then
  ERROR_CODE=$(echo "$BODY" | jq -r '.base_resp.status_code' 2>/dev/null)
  
  if [ "$ERROR_CODE" != "0" ]; then
    echo "❌ API Error: $(echo "$BODY" | jq -r '.base_resp.status_msg' 2>/dev/null)"
    exit 1
  fi
  
  TOTAL=$(echo "$BODY" | jq -r '.model_remains[0].current_interval_total_count' 2>/dev/null)
  REMAINS=$(echo "$BODY" | jq -r '.model_remains[0].current_interval_usage_count' 2>/dev/null)
  REMAINS_TIME=$(echo "$BODY" | jq -r '.model_remains[0].remains_time' 2>/dev/null)
  MODEL=$(echo "$BODY" | jq -r '.model_remains[0].model_name' 2>/dev/null)
  
  if [ "$TOTAL" != "null" ] && [ "$REMAINS" != "null" ]; then
    USED=$((TOTAL - REMAINS))
    PERCENT=$((USED * 100 / TOTAL))
    
    # Calculate reset time
    HOURS=$((REMAINS_TIME / 3600000))
    MINUTES=$(((REMAINS_TIME % 3600000) / 60000))
    
    echo "✅ Usage retrieved successfully:"
    echo ""
    echo "📊 Coding Plan Status (${MODEL}):"
    echo "   Used:      ${USED} / ${TOTAL} prompts (${PERCENT}%)"
    echo "   Remaining: ${REMAINS} prompts"
    echo "   Resets in: ${HOURS}h ${MINUTES}m"
    echo ""
    
    if [ "$PERCENT" -gt 90 ]; then
      echo "🚨 CRITICAL: ${PERCENT}% used! Stop all AI work immediately."
    elif [ "$PERCENT" -gt 75 ]; then
      echo "⚠️  WARNING: ${PERCENT}% used. Approaching limit."
    elif [ "$PERCENT" -gt 60 ]; then
      echo "⚠️  CAUTION: ${PERCENT}% used. Target is 60%."
    else
      echo "💚 GREEN: ${PERCENT}% used. Plenty of buffer."
    fi
  else
    echo "⚠️  Could not parse usage data"
  fi
  
elif [ "$STATUS" = "401" ] || [ "$STATUS" = "403" ]; then
  echo "❌ Authorization failed. Check API key."
elif [ "$STATUS" = "500" ] || [ "$STATUS" = "502" ]; then
  echo "⚠️  Server error. Try again later."
else
  echo "❌ Error (HTTP $STATUS)"
fi
