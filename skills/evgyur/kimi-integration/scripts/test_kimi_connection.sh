#!/usr/bin/env bash
# Test Kimi API connection

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=== Kimi API Connection Test ==="
echo

# Check Moonshot API key
if [ -z "$MOONSHOT_API_KEY" ]; then
  echo -e "${YELLOW}⚠️  MOONSHOT_API_KEY not set${NC}"
  echo "   Set it with: export MOONSHOT_API_KEY='sk-...'"
else
  echo -e "${GREEN}✓${NC} MOONSHOT_API_KEY is set"
  
  # Test Moonshot API
  echo "  Testing Moonshot API..."
  response=$(curl -s -X POST "https://api.moonshot.cn/v1/chat/completions" \
    -H "Authorization: Bearer $MOONSHOT_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "kimi-k2.5",
      "messages": [{"role": "user", "content": "test"}],
      "max_tokens": 10
    }')
  
  if echo "$response" | grep -q '"choices"'; then
    echo -e "  ${GREEN}✓${NC} Moonshot API is working"
  else
    echo -e "  ${RED}✗${NC} Moonshot API error:"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
  fi
fi

echo

# Check Kimi Code API key
if [ -z "$KIMICODE_API_KEY" ]; then
  echo -e "${YELLOW}⚠️  KIMICODE_API_KEY not set${NC}"
  echo "   Set it with: export KIMICODE_API_KEY='sk-...'"
else
  echo -e "${GREEN}✓${NC} KIMICODE_API_KEY is set"
  
  # Test Kimi Code API
  echo "  Testing Kimi Code API..."
  response=$(curl -s -X POST "https://api.kimi.com/coding/v1/chat/completions" \
    -H "Authorization: Bearer $KIMICODE_API_KEY" \
    -H "Content-Type: application/json" \
    -d '{
      "model": "kimi-for-coding",
      "messages": [{"role": "user", "content": "test"}],
      "max_tokens": 10
    }')
  
  if echo "$response" | grep -q '"choices"'; then
    echo -e "  ${GREEN}✓${NC} Kimi Code API is working"
  else
    echo -e "  ${RED}✗${NC} Kimi Code API error:"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
  fi
fi

echo
echo "=== Test Complete ==="
