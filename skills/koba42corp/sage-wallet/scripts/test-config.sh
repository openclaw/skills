#!/usr/bin/env bash
# test-config.sh — Tests for sage-config.sh
# Run: ./test-config.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the config functions
source "$SCRIPT_DIR/sage-config.sh"

# Test temp directory
TEST_DIR=$(mktemp -d)
export SAGE_CONFIG_DIR="$TEST_DIR"
export SAGE_CONFIG_FILE="$TEST_DIR/config.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

PASSED=0
FAILED=0

pass() {
  echo -e "${GREEN}✓${NC} $1"
  PASSED=$((PASSED + 1))
}

fail() {
  echo -e "${RED}✗${NC} $1"
  FAILED=$((FAILED + 1))
}

cleanup() {
  rm -rf "$TEST_DIR"
}
trap cleanup EXIT

echo "=== Sage Config Tests ==="
echo "Test dir: $TEST_DIR"
echo ""

# Test 1: Platform detection
echo "--- Platform Detection ---"
platform=$(detect_platform)
if [[ "$platform" =~ ^(mac|linux|windows)$ ]]; then
  pass "detect_platform returns valid platform: $platform"
else
  fail "detect_platform returned invalid: $platform"
fi

# Test 2: Default paths
echo ""
echo "--- Default Paths ---"
cert_mac=$(get_default_cert_path "mac")
if [[ "$cert_mac" == *"Library/Application Support"*"wallet.crt" ]]; then
  pass "Mac cert path correct"
else
  fail "Mac cert path wrong: $cert_mac"
fi

cert_linux=$(get_default_cert_path "linux")
if [[ "$cert_linux" == *".local/share/sage"*"wallet.crt" ]]; then
  pass "Linux cert path correct"
else
  fail "Linux cert path wrong: $cert_linux"
fi

key_linux=$(get_default_key_path "linux")
if [[ "$key_linux" == *".local/share/sage"*"wallet.key" ]]; then
  pass "Linux key path correct"
else
  fail "Linux key path wrong: $key_linux"
fi

# Test 3: Config initialization
echo ""
echo "--- Config Init ---"
init_config > /dev/null
if [[ -f "$SAGE_CONFIG_FILE" ]]; then
  pass "Config file created"
else
  fail "Config file not created"
fi

# Verify JSON structure
if jq -e '.platform' "$SAGE_CONFIG_FILE" > /dev/null 2>&1; then
  pass "Config has valid JSON with platform field"
else
  fail "Config JSON invalid"
fi

# Test 4: Get config defaults
echo ""
echo "--- Get Config ---"
rpc_url=$(get_config "rpc_url")
if [[ "$rpc_url" == "https://127.0.0.1:9257" ]]; then
  pass "Default rpc_url correct"
else
  fail "Default rpc_url wrong: $rpc_url"
fi

platform_val=$(get_config "platform")
if [[ "$platform_val" == "auto" ]]; then
  pass "Default platform correct"
else
  fail "Default platform wrong: $platform_val"
fi

# Test 5: Set config
echo ""
echo "--- Set Config ---"
set_config "rpc_url" "https://custom:9999" > /dev/null
new_rpc=$(get_config "rpc_url")
if [[ "$new_rpc" == "https://custom:9999" ]]; then
  pass "Set rpc_url works"
else
  fail "Set rpc_url failed: $new_rpc"
fi

set_config "fingerprint" "1234567890" > /dev/null
fp=$(get_config "fingerprint")
if [[ "$fp" == "1234567890" ]]; then
  pass "Set fingerprint works"
else
  fail "Set fingerprint failed: $fp"
fi

set_config "auto_login" "true" > /dev/null
al=$(get_config "auto_login")
if [[ "$al" == "true" ]]; then
  pass "Set boolean works"
else
  fail "Set boolean failed: $al"
fi

# Test 6: Resolve config
echo ""
echo "--- Resolve Config ---"
resolved=$(resolve_config)
if echo "$resolved" | grep -q "SAGE_RPC_URL=https://custom:9999"; then
  pass "Resolve includes custom rpc_url"
else
  fail "Resolve missing custom rpc_url"
fi

if echo "$resolved" | grep -q "SAGE_FINGERPRINT=1234567890"; then
  pass "Resolve includes fingerprint"
else
  fail "Resolve missing fingerprint"
fi

# Test 7: Reset config
echo ""
echo "--- Reset Config ---"
reset_config > /dev/null
rpc_after_reset=$(get_config "rpc_url")
if [[ "$rpc_after_reset" == "https://127.0.0.1:9257" ]]; then
  pass "Reset restores defaults"
else
  fail "Reset failed: $rpc_after_reset"
fi

# Test 8: Null handling
echo ""
echo "--- Null Handling ---"
cert_null=$(get_config "cert_path" "")
if [[ -z "$cert_null" || "$cert_null" == "null" ]]; then
  pass "Null cert_path handled correctly"
else
  fail "Null handling wrong: $cert_null"
fi

# Summary
echo ""
echo "=== Results ==="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [[ $FAILED -gt 0 ]]; then
  exit 1
fi
