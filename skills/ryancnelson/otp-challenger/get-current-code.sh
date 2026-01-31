#!/bin/bash
# Get current valid OTP code
#
# Usage: get-current-code.sh [secret]
#
# If secret not provided, reads from OTP_SECRET env or config

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw}"
CONFIG_FILE="${OPENCLAW_CONFIG:-$HOME/.openclaw/config.yaml}"

SECRET="${1:-${OTP_SECRET:-}}"

# If no secret provided, try to read from config
if [ -z "$SECRET" ] && [ -f "$CONFIG_FILE" ]; then
  SECRET=$(grep -A5 "^security:" "$CONFIG_FILE" | grep "secret:" | awk '{print $2}' | tr -d '"' | head -1)
fi

if [ -z "$SECRET" ]; then
  echo "ERROR: No secret provided" >&2
  echo "Usage: get-current-code.sh [secret]" >&2
  echo "Or set OTP_SECRET environment variable" >&2
  exit 1
fi

# Check if oathtool is available
if ! command -v oathtool &> /dev/null; then
  echo "ERROR: oathtool not found. Install with:" >&2
  echo "  macOS:  brew install oath-toolkit" >&2
  echo "  Fedora: sudo dnf install oathtool" >&2
  echo "  Ubuntu: sudo apt-get install oathtool" >&2
  exit 1
fi

# Generate current code
CODE=$(oathtool --totp -b "$SECRET" 2>/dev/null)
if [ "$?" -ne 0 ]; then
  echo "ERROR: Failed to generate TOTP. Check secret format (base32)." >&2
  exit 1
fi

echo "$CODE"
