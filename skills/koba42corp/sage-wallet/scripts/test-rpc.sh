#!/usr/bin/env bash
# test-rpc.sh — Tests for sage-rpc.sh
# Run: ./test-rpc.sh [--live]
#
# By default runs dry/mock tests only.
# Use --live to test against a running Sage instance.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIVE_MODE=false

for arg in "$@"; do
  case "$arg" in
    --live) LIVE_MODE=true ;;
  esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0

pass() {
  echo -e "${GREEN}✓${NC} $1"
  PASSED=$((PASSED + 1))
}

fail() {
  echo -e "${RED}✗${NC} $1"
  FAILED=$((FAILED + 1))
}

skip() {
  echo -e "${YELLOW}○${NC} $1 (skipped)"
  SKIPPED=$((SKIPPED + 1))
}

echo "=== Sage RPC Tests ==="
echo "Mode: $([ "$LIVE_MODE" = true ] && echo "LIVE" || echo "DRY")"
echo ""

# Test 1: Script sources without error
echo "--- Script Loading ---"
if source "$SCRIPT_DIR/sage-rpc.sh" 2>/dev/null; then
  pass "sage-rpc.sh sources without error"
else
  fail "sage-rpc.sh failed to source"
  exit 1
fi

# Test 2: load_config function exists
if declare -f load_config > /dev/null; then
  pass "load_config function exists"
else
  fail "load_config function missing"
fi

# Test 3: sage_rpc function exists
if declare -f sage_rpc > /dev/null; then
  pass "sage_rpc function exists"
else
  fail "sage_rpc function missing"
fi

# Test 4: sage_test_connection function exists
if declare -f sage_test_connection > /dev/null; then
  pass "sage_test_connection function exists"
else
  fail "sage_test_connection function missing"
fi

# Test 5: Config resolution
echo ""
echo "--- Config Resolution ---"

# Create temp config
TEST_DIR=$(mktemp -d)
export SAGE_CONFIG_DIR="$TEST_DIR"
mkdir -p "$TEST_DIR"
cat > "$TEST_DIR/config.json" << 'EOF'
{
  "platform": "linux",
  "rpc_url": "https://127.0.0.1:9257",
  "cert_path": "/tmp/test.crt",
  "key_path": "/tmp/test.key",
  "fingerprint": null,
  "auto_login": false
}
EOF

# Force reload
unset SAGE_RPC_URL SAGE_CERT_PATH SAGE_KEY_PATH 2>/dev/null || true
load_config

if [[ "$SAGE_RPC_URL" == "https://127.0.0.1:9257" ]]; then
  pass "RPC URL loaded from config"
else
  fail "RPC URL not loaded: $SAGE_RPC_URL"
fi

if [[ "$SAGE_CERT_PATH" == "/tmp/test.crt" ]]; then
  pass "Cert path loaded from config"
else
  fail "Cert path not loaded: $SAGE_CERT_PATH"
fi

rm -rf "$TEST_DIR"

# Live tests
echo ""
echo "--- Live Connection Tests ---"

if [[ "$LIVE_MODE" != true ]]; then
  skip "Connection test (use --live)"
  skip "Version check (use --live)"
  skip "Sync status (use --live)"
  skip "Keys list (use --live)"
else
  # Reset to real config
  unset SAGE_CONFIG_DIR SAGE_RPC_URL SAGE_CERT_PATH SAGE_KEY_PATH
  load_config
  
  # Test connection
  echo "Testing connection to $SAGE_RPC_URL..."
  
  if [[ ! -f "$SAGE_CERT_PATH" ]]; then
    fail "Certificate not found at $SAGE_CERT_PATH"
  elif [[ ! -f "$SAGE_KEY_PATH" ]]; then
    fail "Key not found at $SAGE_KEY_PATH"
  else
    pass "Certificates found"
    
    # Version check
    version_resp=$(sage_rpc "get_version" '{}' 2>&1) || true
    if echo "$version_resp" | jq -e '.version' > /dev/null 2>&1; then
      version=$(echo "$version_resp" | jq -r '.version')
      pass "Version check: Sage $version"
    else
      fail "Version check failed: $version_resp"
    fi
    
    # Sync status
    sync_resp=$(sage_rpc "get_sync_status" '{}' 2>&1) || true
    if echo "$sync_resp" | jq -e '.balance' > /dev/null 2>&1; then
      pass "Sync status returns valid response"
    else
      fail "Sync status failed: $sync_resp"
    fi
    
    # Keys list (may require login)
    keys_resp=$(sage_rpc "get_keys" '{}' 2>&1) || true
    if echo "$keys_resp" | jq -e '.keys' > /dev/null 2>&1; then
      key_count=$(echo "$keys_resp" | jq '.keys | length')
      pass "Keys list: $key_count wallet(s) found"
    else
      # May fail if not logged in - that's ok
      skip "Keys list (may need login)"
    fi
  fi
fi

# Summary
echo ""
echo "=== Results ==="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"

if [[ $FAILED -gt 0 ]]; then
  exit 1
fi
