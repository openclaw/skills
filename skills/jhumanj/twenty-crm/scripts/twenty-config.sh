#!/bin/bash
set -euo pipefail

# Loads config for Twenty CRM API scripts.
# Expected file: /Users/jhumanj/clawd/config/twenty.env

CONFIG_FILE="/Users/jhumanj/clawd/config/twenty.env"

if [ -f "$CONFIG_FILE" ]; then
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
fi

if [ -z "${TWENTY_BASE_URL:-}" ]; then
  echo "Missing TWENTY_BASE_URL. Create $CONFIG_FILE (see /Users/jhumanj/clawd/config/twenty.env.example)." >&2
  exit 1
fi

if [ -z "${TWENTY_API_KEY:-}" ]; then
  echo "Missing TWENTY_API_KEY. Create $CONFIG_FILE (see /Users/jhumanj/clawd/config/twenty.env.example)." >&2
  exit 1
fi

# Normalize trailing slash
TWENTY_BASE_URL="${TWENTY_BASE_URL%/}"

export TWENTY_BASE_URL
export TWENTY_API_KEY
