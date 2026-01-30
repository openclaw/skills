#!/usr/bin/env bash
# sage-rpc.sh — RPC caller for Sage Wallet with mTLS support
# Source this file to use sage_rpc function, or run directly

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load config if not already set
load_config() {
  if [[ -z "${SAGE_RPC_URL:-}" ]]; then
    if [[ -f "$SCRIPT_DIR/sage-config.sh" ]]; then
      eval "$("$SCRIPT_DIR/sage-config.sh" resolve)"
    else
      # Fallback defaults
      SAGE_RPC_URL="https://127.0.0.1:9257"
      SAGE_CERT_PATH="$HOME/.local/share/sage/ssl/wallet.crt"
      SAGE_KEY_PATH="$HOME/.local/share/sage/ssl/wallet.key"
    fi
  fi
}

# Make an RPC call to Sage wallet
# Usage: sage_rpc <endpoint> [payload] [--fingerprint fp] [--rpc url] [--cert path] [--key path]
sage_rpc() {
  load_config
  
  local endpoint=""
  local payload="{}"
  local rpc_url="$SAGE_RPC_URL"
  local cert_path="$SAGE_CERT_PATH"
  local key_path="$SAGE_KEY_PATH"
  
  # Parse arguments
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --rpc)
        rpc_url="$2"
        shift 2
        ;;
      --cert)
        cert_path="$2"
        shift 2
        ;;
      --key)
        key_path="$2"
        shift 2
        ;;
      --fingerprint)
        # Inject fingerprint into payload if needed
        shift 2
        ;;
      -*)
        echo "Unknown option: $1" >&2
        return 1
        ;;
      *)
        if [[ -z "$endpoint" ]]; then
          endpoint="$1"
        else
          payload="$1"
        fi
        shift
        ;;
    esac
  done
  
  if [[ -z "$endpoint" ]]; then
    echo "Usage: sage_rpc <endpoint> [payload] [options]" >&2
    return 1
  fi
  
  # Validate cert/key exist
  if [[ ! -f "$cert_path" ]]; then
    echo "Error: Certificate not found at $cert_path" >&2
    echo "Configure with: sage-config.sh cert /path/to/wallet.crt" >&2
    return 1
  fi
  
  if [[ ! -f "$key_path" ]]; then
    echo "Error: Key not found at $key_path" >&2
    echo "Configure with: sage-config.sh key /path/to/wallet.key" >&2
    return 1
  fi
  
  # Make the RPC call
  local response
  response=$(curl -s -X POST \
    --cert "$cert_path" \
    --key "$key_path" \
    --cacert "$cert_path" \
    -H "Content-Type: application/json" \
    -d "$payload" \
    "${rpc_url}/${endpoint}" 2>&1) || {
      echo "Error: RPC call failed" >&2
      echo "$response" >&2
      return 1
    }
  
  echo "$response"
}

# Test connection to Sage wallet
sage_test_connection() {
  load_config
  
  echo "Testing connection to $SAGE_RPC_URL..."
  echo "  Cert: $SAGE_CERT_PATH"
  echo "  Key:  $SAGE_KEY_PATH"
  echo ""
  
  local response
  if response=$(sage_rpc "get_version" '{}' 2>&1); then
    local version
    version=$(echo "$response" | jq -r '.version // empty' 2>/dev/null || echo "")
    if [[ -n "$version" ]]; then
      echo "✓ Connected! Sage version $version"
      return 0
    else
      echo "✗ Unexpected response: $response"
      return 1
    fi
  else
    echo "✗ Connection failed: $response"
    return 1
  fi
}

# Get sync status
sage_sync_status() {
  local response
  response=$(sage_rpc "get_sync_status" '{}')
  echo "$response" | jq '.'
}

# Login to wallet
sage_login() {
  local fingerprint="${1:-${SAGE_FINGERPRINT:-}}"
  
  if [[ -z "$fingerprint" ]]; then
    echo "Error: Fingerprint required" >&2
    echo "Usage: sage_login <fingerprint>" >&2
    return 1
  fi
  
  sage_rpc "login" "{\"fingerprint\": $fingerprint}"
}

# Logout from wallet
sage_logout() {
  sage_rpc "logout" '{}'
}

# List keys
sage_keys() {
  sage_rpc "get_keys" '{}'
}

# If run directly (not sourced), execute command
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  cmd="${1:-help}"
  shift || true
  
  case "$cmd" in
    test)
      sage_test_connection
      ;;
    sync)
      sage_sync_status
      ;;
    login)
      sage_login "$@"
      ;;
    logout)
      sage_logout
      ;;
    keys)
      sage_keys
      ;;
    call)
      sage_rpc "$@"
      ;;
    help|--help|-h)
      echo "Usage: sage-rpc.sh <command> [args]"
      echo ""
      echo "Commands:"
      echo "  test              Test connection to Sage wallet"
      echo "  sync              Get sync status"
      echo "  login <fp>        Login with fingerprint"
      echo "  logout            Logout"
      echo "  keys              List wallet keys"
      echo "  call <ep> [json]  Call arbitrary endpoint"
      echo ""
      echo "Source this file to use sage_rpc function:"
      echo "  source sage-rpc.sh"
      echo "  sage_rpc get_version '{}'"
      ;;
    *)
      echo "Unknown command: $cmd"
      exit 1
      ;;
  esac
fi
