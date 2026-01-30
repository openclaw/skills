#!/usr/bin/env bash
# test-integration.sh — Full integration tests against live Sage wallet
# 
# WARNING: These tests interact with a real wallet!
# Only run on testnet or with a test wallet.
#
# Usage: ./test-integration.sh [--testnet] [--fingerprint FP]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/sage-rpc.sh"

FINGERPRINT=""
NETWORK="mainnet"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --testnet) NETWORK="testnet11"; shift ;;
    --fingerprint) FINGERPRINT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0

pass() { echo -e "${GREEN}✓${NC} $1"; PASSED=$((PASSED + 1)); }
fail() { echo -e "${RED}✗${NC} $1"; FAILED=$((FAILED + 1)); }
skip() { echo -e "${YELLOW}○${NC} $1"; SKIPPED=$((SKIPPED + 1)); }
info() { echo -e "${BLUE}ℹ${NC} $1"; }

echo "=========================================="
echo "  Sage Wallet Integration Tests"
echo "=========================================="
echo ""

# Pre-flight checks
echo "--- Pre-flight Checks ---"

load_config

if [[ ! -f "$SAGE_CERT_PATH" ]]; then
  echo -e "${RED}Certificate not found: $SAGE_CERT_PATH${NC}"
  echo "Configure with: sage-config.sh cert /path/to/wallet.crt"
  exit 1
fi

if [[ ! -f "$SAGE_KEY_PATH" ]]; then
  echo -e "${RED}Key not found: $SAGE_KEY_PATH${NC}"
  echo "Configure with: sage-config.sh key /path/to/wallet.key"
  exit 1
fi

pass "Certificates found"

# Test connection
version_resp=$(sage_rpc "get_version" '{}' 2>&1) || true
if ! echo "$version_resp" | jq -e '.version' > /dev/null 2>&1; then
  echo -e "${RED}Cannot connect to Sage wallet${NC}"
  echo "Response: $version_resp"
  exit 1
fi
VERSION=$(echo "$version_resp" | jq -r '.version')
pass "Connected to Sage $VERSION"

echo ""
echo "--- System Tests ---"

# Get sync status
sync_resp=$(sage_rpc "get_sync_status" '{}')
if echo "$sync_resp" | jq -e '.balance' > /dev/null 2>&1; then
  balance=$(echo "$sync_resp" | jq -r '.balance')
  synced=$(echo "$sync_resp" | jq -r '.synced_coins')
  total=$(echo "$sync_resp" | jq -r '.total_coins')
  pass "Sync status: $synced/$total coins synced"
  info "Balance: $balance mojos"
else
  fail "Sync status failed"
fi

# Database stats
db_resp=$(sage_rpc "get_database_stats" '{}')
if echo "$db_resp" | jq -e '.database_size_bytes' > /dev/null 2>&1; then
  size=$(echo "$db_resp" | jq -r '.database_size_bytes')
  size_mb=$((size / 1024 / 1024))
  pass "Database stats: ${size_mb}MB"
else
  fail "Database stats failed"
fi

echo ""
echo "--- Key Management Tests ---"

# List keys
keys_resp=$(sage_rpc "get_keys" '{}')
if echo "$keys_resp" | jq -e '.keys' > /dev/null 2>&1; then
  key_count=$(echo "$keys_resp" | jq '.keys | length')
  pass "Found $key_count wallet key(s)"
  
  if [[ $key_count -gt 0 ]]; then
    # Get first key fingerprint if not provided
    if [[ -z "$FINGERPRINT" ]]; then
      FINGERPRINT=$(echo "$keys_resp" | jq -r '.keys[0].fingerprint')
      info "Using first wallet: $FINGERPRINT"
    fi
  fi
else
  fail "List keys failed"
fi

# Login test (if we have a fingerprint)
if [[ -n "$FINGERPRINT" ]]; then
  login_resp=$(sage_rpc "login" "{\"fingerprint\": $FINGERPRINT}")
  if [[ "$login_resp" == "{}" ]] || echo "$login_resp" | jq -e '.' > /dev/null 2>&1; then
    pass "Login successful: $FINGERPRINT"
  else
    fail "Login failed: $login_resp"
  fi
else
  skip "Login test (no fingerprint)"
fi

echo ""
echo "--- Network Tests ---"

# Get network
network_resp=$(sage_rpc "get_network" '{}')
if echo "$network_resp" | jq -e '.network' > /dev/null 2>&1; then
  net_name=$(echo "$network_resp" | jq -r '.network.name')
  net_kind=$(echo "$network_resp" | jq -r '.kind')
  pass "Network: $net_name ($net_kind)"
else
  fail "Get network failed"
fi

# Get peers
peers_resp=$(sage_rpc "get_peers" '{}')
if echo "$peers_resp" | jq -e '.peers' > /dev/null 2>&1; then
  peer_count=$(echo "$peers_resp" | jq '.peers | length')
  pass "Connected to $peer_count peer(s)"
else
  fail "Get peers failed"
fi

echo ""
echo "--- Data Query Tests ---"

# Get coins (limited)
coins_resp=$(sage_rpc "get_coins" '{"offset": 0, "limit": 5, "filter_mode": "selectable"}')
if echo "$coins_resp" | jq -e '.coins' > /dev/null 2>&1; then
  coin_count=$(echo "$coins_resp" | jq '.coins | length')
  total_coins=$(echo "$coins_resp" | jq -r '.total')
  pass "Coins: showing $coin_count of $total_coins"
else
  fail "Get coins failed"
fi

# Get CATs
cats_resp=$(sage_rpc "get_cats" '{}')
if echo "$cats_resp" | jq -e '.cats' > /dev/null 2>&1; then
  cat_count=$(echo "$cats_resp" | jq '.cats | length')
  pass "CAT tokens: $cat_count"
else
  fail "Get CATs failed"
fi

# Get NFTs (limited)
nfts_resp=$(sage_rpc "get_nfts" '{"offset": 0, "limit": 5, "sort_mode": "recent", "include_hidden": false}')
if echo "$nfts_resp" | jq -e '.nfts' > /dev/null 2>&1; then
  nft_count=$(echo "$nfts_resp" | jq '.nfts | length')
  total_nfts=$(echo "$nfts_resp" | jq -r '.total')
  pass "NFTs: showing $nft_count of $total_nfts"
else
  fail "Get NFTs failed"
fi

# Get DIDs
dids_resp=$(sage_rpc "get_dids" '{}')
if echo "$dids_resp" | jq -e '.dids' > /dev/null 2>&1; then
  did_count=$(echo "$dids_resp" | jq '.dids | length')
  pass "DIDs: $did_count"
else
  fail "Get DIDs failed"
fi

# Get offers
offers_resp=$(sage_rpc "get_offers" '{}')
if echo "$offers_resp" | jq -e '.offers' > /dev/null 2>&1; then
  offer_count=$(echo "$offers_resp" | jq '.offers | length')
  pass "Offers: $offer_count"
else
  fail "Get offers failed"
fi

# Get transactions (limited)
txns_resp=$(sage_rpc "get_transactions" '{"offset": 0, "limit": 5, "ascending": false}')
if echo "$txns_resp" | jq -e '.transactions' > /dev/null 2>&1; then
  txn_count=$(echo "$txns_resp" | jq '.transactions | length')
  total_txns=$(echo "$txns_resp" | jq -r '.total')
  pass "Transactions: showing $txn_count of $total_txns"
else
  fail "Get transactions failed"
fi

# Pending transactions
pending_resp=$(sage_rpc "get_pending_transactions" '{}')
if echo "$pending_resp" | jq -e '.transactions' > /dev/null 2>&1; then
  pending_count=$(echo "$pending_resp" | jq '.transactions | length')
  pass "Pending transactions: $pending_count"
else
  fail "Get pending transactions failed"
fi

echo ""
echo "--- Address Tests ---"

# Check a known good address format
check_resp=$(sage_rpc "check_address" '{"address": "xch1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqm6ksh7qddh"}')
if echo "$check_resp" | jq -e '.valid' > /dev/null 2>&1; then
  valid=$(echo "$check_resp" | jq -r '.valid')
  pass "Address validation works (valid=$valid)"
else
  fail "Address check failed"
fi

# Get derivations
deriv_resp=$(sage_rpc "get_derivations" '{"hardened": false, "offset": 0, "limit": 3}')
if echo "$deriv_resp" | jq -e '.derivations' > /dev/null 2>&1; then
  deriv_count=$(echo "$deriv_resp" | jq '.derivations | length')
  pass "Derivations: $deriv_count addresses"
else
  fail "Get derivations failed"
fi

# Logout
if [[ -n "$FINGERPRINT" ]]; then
  logout_resp=$(sage_rpc "logout" '{}')
  pass "Logout completed"
fi

# Summary
echo ""
echo "=========================================="
echo "  Results"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

if [[ $FAILED -gt 0 ]]; then
  echo -e "${RED}Some tests failed!${NC}"
  exit 1
else
  echo -e "${GREEN}All tests passed!${NC}"
fi
