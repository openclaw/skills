#!/usr/bin/env bash
# UniFi API helper - handles login and authenticated calls
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${UNIFI_CONFIG_FILE:-$HOME/.clawdbot/credentials/unifi/config.json}"

# Load config
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Error: UniFi not configured. Create $CONFIG_FILE with {\"url\": \"https://...\", \"username\": \"...\", \"password\": \"...\", \"site\": \"default\"}" >&2
  exit 1
fi

UNIFI_URL=$(jq -r '.url' "$CONFIG_FILE")
UNIFI_USER=$(jq -r '.username' "$CONFIG_FILE")
UNIFI_PASS=$(jq -r '.password' "$CONFIG_FILE")
UNIFI_SITE=$(jq -r '.site // "default"' "$CONFIG_FILE")

# Login and store cookie
# Usage: unifi_login [cookie_file_path]
unifi_login() {
  local cookie_file="${1:-${UNIFI_COOKIE_FILE:-$(mktemp)}}"
  
  # If it's a temp file we created just now, export it so subsequent calls use it
  if [ -z "${UNIFI_COOKIE_FILE:-}" ]; then
      export UNIFI_COOKIE_FILE="$cookie_file"
  fi

  local payload
  payload=$(jq -nc --arg username "$UNIFI_USER" --arg password "$UNIFI_PASS" '{username:$username,password:$password}')
  
  # Try login
  curl -sk -c "$cookie_file" \
    -H "Content-Type: application/json" \
    -X POST \
    "$UNIFI_URL/api/auth/login" \
    --data "$payload" >/dev/null

  if [ ! -s "$cookie_file" ]; then
    echo "Error: Login failed (empty cookie file)" >&2
    return 1
  fi
}

# Make authenticated GET request
# Usage: unifi_get <endpoint>
# Endpoint should be like "stat/sta" or "rest/portforward" - site path is added automatically
# Uses UNIFI_COOKIE_FILE if set, otherwise logs in temporarily
unifi_get() {
  local endpoint="$1"
  local temp_cookie=false
  
  # Ensure we have a cookie
  if [ -z "${UNIFI_COOKIE_FILE:-}" ] || [ ! -f "$UNIFI_COOKIE_FILE" ]; then
    temp_cookie=true
    export UNIFI_COOKIE_FILE=$(mktemp)
    unifi_login "$UNIFI_COOKIE_FILE"
  fi
  
  # Handle both old format (/api/s/site/...) and new format (stat/...)
  local full_url
  if [[ "$endpoint" == /api/* ]]; then
    # Old format - use as-is with proxy/network prefix
    full_url="$UNIFI_URL/proxy/network$endpoint"
  else
    # New format - add full path
    full_url="$UNIFI_URL/proxy/network/api/s/$UNIFI_SITE/$endpoint"
  fi
  
  curl -sk -b "$UNIFI_COOKIE_FILE" "$full_url"
  
  # Cleanup if we created a temp cookie just for this request
  if [ "$temp_cookie" = true ]; then
    rm -f "$UNIFI_COOKIE_FILE"
    unset UNIFI_COOKIE_FILE
  fi
}

export -f unifi_login
export -f unifi_get
export UNIFI_URL UNIFI_SITE
