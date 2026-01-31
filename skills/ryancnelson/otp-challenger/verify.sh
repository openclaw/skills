#!/bin/bash
# Verify an OTP code and update verification state
#
# Usage: verify.sh <user_id> <code>
#
# Exit codes:
#   0 - Valid code, user verified
#   1 - Invalid code
#   2 - Config/setup error

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw}"
STATE_FILE="$WORKSPACE/memory/otp-state.json"
CONFIG_FILE="${CONFIG_FILE:-${OPENCLAW_CONFIG:-$HOME/.openclaw/config.yaml}}"
AUDIT_LOG="${OTP_AUDIT_LOG:-$WORKSPACE/memory/otp-audit.log}"

# Audit logging function
audit_log() {
  local event="$1"
  local user_id="$2"
  local result="$3"
  local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  mkdir -p "$(dirname "$AUDIT_LOG")"
  echo "$timestamp user=$user_id event=$event result=$result" >> "$AUDIT_LOG"
}

# Record verification failure (for rate limiting)
record_failure() {
  local user_id="$1"
  local now_ms="$2"

  # Ensure state file and directory exist
  mkdir -p "$(dirname "$STATE_FILE")"
  if [ ! -f "$STATE_FILE" ]; then
    echo '{"verifications":{},"usedCodes":{},"failureCounts":{}}' > "$STATE_FILE"
  fi

  LOCK_FILE="$STATE_FILE.lock"
  (
    flock -x 200
    jq --arg userId "$user_id" \
       --arg nowMs "$now_ms" \
       '.failureCounts[$userId].count = ((.failureCounts[$userId].count // 0) + 1) |
        .failureCounts[$userId].since = (if .failureCounts[$userId].since then .failureCounts[$userId].since else ($nowMs | tonumber) end)' \
       "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"
  ) 200>"$LOCK_FILE"
}

# Reset failure count on successful verification
reset_failures() {
  local user_id="$1"

  # This is called within the flock block, so no need for separate locking
  # Just ensure we remove the failure count
}

USER_ID="${1}"
CODE="${2}"

if [ -z "$USER_ID" ] || [ -z "$CODE" ]; then
  echo "Usage: verify.sh <user_id> <code>" >&2
  exit 2
fi

# Validate OTP code format (must be exactly 6 digits)
if ! [[ "$CODE" =~ ^[0-9]{6}$ ]]; then
  echo "ERROR: Code must be exactly 6 digits" >&2
  exit 2
fi

# Validate user ID (alphanumeric + @._- only, 1-255 chars)
if [ "${#USER_ID}" -gt 255 ]; then
  echo "ERROR: User ID exceeds maximum length (255 characters)" >&2
  exit 2
fi

if ! [[ "$USER_ID" =~ ^[a-zA-Z0-9@._-]+$ ]]; then
  echo "ERROR: Invalid characters in user ID (allowed: a-z A-Z 0-9 @ . _ -)" >&2
  exit 2
fi

# Get secret from environment or config
SECRET="${OTP_SECRET:-}"
if [ -z "$SECRET" ] && [ -f "$CONFIG_FILE" ]; then
  # Use secure YAML parsing with Python
  if command -v python3 &>/dev/null; then
    SECRET=$(python3 -c "
import sys
try:
    import yaml
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    secret = config.get('security', {}).get('otp', {}).get('secret', '')
    print(secret if secret else '')
except Exception:
    pass
" 2>/dev/null)
  fi
fi

if [ -z "$SECRET" ]; then
  echo "ERROR: OTP_SECRET not set. Configure in environment or ~/.openclaw/config.yaml" >&2
  exit 2
fi

# Validate secret format (base32: A-Z, 2-7, optional = padding, 16-128 chars)
if [ "${#SECRET}" -lt 16 ] || [ "${#SECRET}" -gt 128 ]; then
  echo "ERROR: Secret length must be 16-128 characters" >&2
  exit 2
fi

if ! [[ "$SECRET" =~ ^[A-Z2-7]+=*$ ]]; then
  echo "ERROR: Secret must be base32 encoded (A-Z, 2-7, optional = padding)" >&2
  exit 2
fi

# Check if oathtool is available
if ! command -v oathtool &> /dev/null; then
  echo "ERROR: oathtool not found. Install with:" >&2
  echo "  macOS:  brew install oath-toolkit" >&2
  echo "  Fedora: sudo dnf install oathtool" >&2
  echo "  Ubuntu: sudo apt-get install oathtool" >&2
  exit 2
fi

# Set up state file and check rate limiting BEFORE TOTP validation
mkdir -p "$(dirname "$STATE_FILE")"

# Create state file if it doesn't exist, or recover from corruption
if [ ! -f "$STATE_FILE" ]; then
  echo '{"verifications":{},"usedCodes":{},"failureCounts":{}}' > "$STATE_FILE"
else
  # Validate JSON structure, recover if corrupted
  if ! jq empty "$STATE_FILE" 2>/dev/null; then
    echo "WARN: State file corrupted, reinitializing" >&2
    echo '{"verifications":{},"usedCodes":{},"failureCounts":{}}' > "$STATE_FILE"
  elif ! jq -e '.verifications' "$STATE_FILE" >/dev/null 2>&1; then
    echo "WARN: State file has wrong structure, fixing" >&2
    jq '. + {verifications: {}, usedCodes: {}, failureCounts: {}}' "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
  fi
fi

# Get current time for rate limiting and expiration
NOW_MS=$(date +%s)000

# Check rate limiting (default: 3 failures within 5 minutes)
MAX_FAILURES="${OTP_MAX_FAILURES:-3}"
if [ -f "$STATE_FILE" ]; then
  FAILURE_COUNT=$(jq -r --arg userId "$USER_ID" '.failureCounts[$userId].count // 0' "$STATE_FILE")
  FAILURE_SINCE=$(jq -r --arg userId "$USER_ID" '.failureCounts[$userId].since // 0' "$STATE_FILE")
  RATE_LIMIT_WINDOW=$((5 * 60 * 1000))  # 5 minutes in milliseconds

  if [ "$FAILURE_COUNT" -ge "$MAX_FAILURES" ]; then
    # Check if still within rate limit window
    TIME_SINCE=$((NOW_MS - FAILURE_SINCE))
    if [ "$TIME_SINCE" -lt "$RATE_LIMIT_WINDOW" ]; then
      audit_log "VERIFY" "$USER_ID" "VERIFY_FAIL"
      echo "❌ Too many attempts. Try again later." >&2
      exit 1
    fi
  fi
fi

# Validate the code using oathtool
EXPECTED=$(oathtool --totp -b "$SECRET" 2>/dev/null)
if [ "$?" -ne 0 ]; then
  echo "ERROR: Failed to generate TOTP. Check secret format (base32)." >&2
  exit 2
fi

if [ "$CODE" != "$EXPECTED" ]; then
  # Try previous and next windows for clock skew
  # Use relative time in seconds: -30 for previous window, +30 for next
  NOW=$(date +%s)
  EXPECTED_PREV=$(oathtool --totp -b "$SECRET" -N "@$((NOW - 30))" 2>/dev/null || true)
  EXPECTED_NEXT=$(oathtool --totp -b "$SECRET" -N "@$((NOW + 30))" 2>/dev/null || true)

  if [ "$CODE" != "$EXPECTED_PREV" ] && [ "$CODE" != "$EXPECTED_NEXT" ]; then
    FAIL_NOW_MS=$(date +%s)000
    record_failure "$USER_ID" "$FAIL_NOW_MS"
    audit_log "VERIFY" "$USER_ID" "VERIFY_FAIL"
    echo "❌ Invalid OTP code" >&2
    exit 1
  fi
fi

# Code is valid - update state

# Get interval hours (default 24)
INTERVAL_HOURS="${OTP_INTERVAL_HOURS:-24}"

# Calculate expiration timestamp (milliseconds)
EXPIRES_MS=$((NOW_MS + (INTERVAL_HOURS * 60 * 60 * 1000)))

# Create code fingerprint for replay protection (user + code + time window)
# Codes expire after 90 seconds (3 TOTP windows)
CODE_WINDOW=$((NOW_MS / 90000))
CODE_KEY="${USER_ID}:${CODE}:${CODE_WINDOW}"
CODE_EXPIRY=$((NOW_MS + 90000))

# Update state using jq with file locking for atomic writes
LOCK_FILE="$STATE_FILE.lock"
(
  # Acquire exclusive lock
  flock -x 200

  # Check if code was already used (replay attack)
  if [ -f "$STATE_FILE" ]; then
    ALREADY_USED=$(jq -r --arg key "$CODE_KEY" '.usedCodes[$key] // empty' "$STATE_FILE" 2>/dev/null)
    if [ -n "$ALREADY_USED" ]; then
      audit_log "VERIFY" "$USER_ID" "VERIFY_FAIL"
      echo "❌ OTP code already used (replay attack prevented)" >&2
      exit 1
    fi
  fi

  # Clean up expired used codes (older than 90 seconds)
  # Update verification, mark code as used, and reset failure count
  jq --arg userId "$USER_ID" \
     --arg verifiedAt "$NOW_MS" \
     --arg expiresAt "$EXPIRES_MS" \
     --arg codeKey "$CODE_KEY" \
     --arg codeExpiry "$CODE_EXPIRY" \
     --arg nowMs "$NOW_MS" \
     '.verifications[$userId] = {verifiedAt: ($verifiedAt | tonumber), expiresAt: ($expiresAt | tonumber)} |
      .usedCodes[$codeKey] = ($codeExpiry | tonumber) |
      .usedCodes |= with_entries(select(.value > ($nowMs | tonumber))) |
      del(.failureCounts[$userId])' \
     "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

) 200>"$LOCK_FILE"

audit_log "VERIFY" "$USER_ID" "VERIFY_SUCCESS"
echo "✅ OTP verified for $USER_ID (valid for $INTERVAL_HOURS hours)"
exit 0
