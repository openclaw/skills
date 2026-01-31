---
name: otp-challenger
version: 1.1.0
description: Enable agents and skills to challenge users for fresh two-factor authentication proof before executing sensitive actions. Use this for identity verification in approval workflows - deploy commands, financial operations, data access, admin operations, and change control.
metadata: {"openclaw": {"emoji": "🔐", "homepage": "https://github.com/ryancnelson/otp-challenger", "requires": {"bins": ["jq", "python3"], "anyBins": ["oathtool", "node"]}, "install": [{"id": "jq", "kind": "brew", "formula": "jq", "bins": ["jq"], "label": "Install jq via Homebrew", "os": ["darwin", "linux"]}, {"id": "python3", "kind": "brew", "formula": "python3", "bins": ["python3"], "label": "Install Python 3 via Homebrew", "os": ["darwin", "linux"]}, {"id": "oathtool", "kind": "brew", "formula": "oath-toolkit", "bins": ["oathtool"], "label": "Install OATH Toolkit via Homebrew", "os": ["darwin", "linux"]}]}}
---

# OTP Identity Challenge Skill

**Purpose:** Enable agents and skills to challenge users for fresh two-factor authentication proof before executing sensitive actions.

## What This Is For

This skill provides **identity verification for approval workflows**. When your agent needs to execute a command with change-control concerns (deploying code, modifying infrastructure, accessing sensitive data, financial transactions), it can challenge the user to prove their identity with a time-based one-time password (TOTP).

This is **not** about securing your chat channel—it's about verifying identity **before specific actions**.

## Use Cases

- **Deploy commands**: Require fresh 2FA before `kubectl apply` or `terraform apply`
- **Financial operations**: Verify identity before wire transfers or payment approvals
- **Data access**: Challenge before exporting customer data or PII
- **Admin operations**: Verify before user account modifications or permission changes
- **Change control**: Enforce approval workflows with cryptographic proof of identity

## How It Works

1. Your agent or skill calls `verify.sh` with the user's ID and their 6-digit code
2. The skill validates the code against your TOTP secret
3. If valid, verification state is recorded with a timestamp
4. Other scripts can check `check-status.sh` to see if verification is still fresh
5. Verification expires after a configured interval (default: 24 hours)

## Installation

### Via ClawHub (recommended)
```bash
clawhub install otp
```

### Manual
```bash
cd ~/.openclaw/skills
git clone https://github.com/ryancnelson/otp-skill.git otp
```

### Check Dependencies
After installation, verify required dependencies:
```bash
# Check what's available
which jq && echo "✅ jq available" || echo "❌ Install: brew install jq"
which python3 && echo "✅ python3 available" || echo "❌ Install: brew install python3"
which oathtool && echo "✅ oathtool available" || echo "❌ Install: brew install oath-toolkit"
```

**Note:** `oathtool` is optional - the skill includes a built-in TOTP generator, but `oathtool` provides additional validation.

## Setup

### 1. Generate a TOTP Secret

Use the included secret generator:
```bash
cd ~/.openclaw/skills/otp
./generate-secret.sh "your-email@example.com"
```

This will display:
- A QR code to scan with your authenticator app
- The base32 secret for manual entry
- Configuration instructions

**Alternative:** Use any other TOTP secret generator. You need a **base32-encoded secret**.

### 2. Scan QR Code

Add the secret to your authenticator app:
- Google Authenticator
- Authy
- 1Password
- Bitwarden
- Any RFC 6238 compatible app

### 3. Store the Secret

**Option A: In your OpenClaw config**
```yaml
# ~/.openclaw/config.yaml
security:
  otp:
    secret: "YOUR_BASE32_SECRET_HERE"
    accountName: "user@example.com"
    issuer: "OpenClaw"
    intervalHours: 24  # Re-verify every 24 hours
```

**Option B: In environment variable**
```bash
export OTP_SECRET="YOUR_BASE32_SECRET_HERE"
```

**Option C: In 1Password** (recommended for security)
```yaml
security:
  otp:
    secret: "op://vault/OpenClaw OTP/totp"
```

### 4. Test Your Setup

After configuring the secret, test that everything works:
```bash
# Get current code from your authenticator app (6 digits)
./verify.sh "testuser" "123456"  # Replace with actual code
# Should show: ✅ OTP verified for testuser (valid for 24 hours)

# Check verification status
./check-status.sh "testuser"
# Should show: ✅ Valid for 23 more hours

# Test error case
./verify.sh "testuser" "000000"
# Should show: ❌ Invalid OTP code
```

### 5. Optional: Run Test Suite

Full test suite available at: https://github.com/ryancnelson/otp-challenger

## Usage

### For Skill Authors

When your skill needs to verify user identity:

```bash
#!/bin/bash
# In your sensitive-action.sh

# Source the OTP skill
source ../otp/verify.sh

USER_ID="$1"
OTP_CODE="$2"

# Challenge the user
if ! verify_otp "$USER_ID" "$OTP_CODE"; then
  echo "❌ OTP verification failed. Run: /otp <code>"
  exit 1
fi

# Proceed with sensitive action
echo "✅ Identity verified. Proceeding with deployment..."
kubectl apply -f production.yaml
```

### Checking Verification Status

```bash
#!/bin/bash
source ../otp/check-status.sh

if check_otp_status "$USER_ID"; then
  echo "✅ User verified within last 24 hours"
else
  echo "⚠️ Verification expired. User must verify again."
fi
```

### For End Users

When prompted by a skill:
```
User: deploy to production
Agent: 🔒 This action requires identity verification. Please provide your OTP code.

User: /otp 123456
Agent: ✅ Identity verified. Deploying to production...
```

## Scripts

- **`verify.sh <user_id> <code>`** - Verify OTP code and update state
- **`check-status.sh <user_id>`** - Check if user verification is still valid
- **`generate-secret.sh <account_name>`** - Generate new TOTP secret
- **`get-current-code.sh <secret>`** - Get current valid code (testing only)

## Configuration

Set these in your OpenClaw config or environment:

- **`OTP_SECRET`** - Base32 TOTP secret (required)
- **`OTP_INTERVAL_HOURS`** - Verification expiry (default: 24)
- **`OTP_GRACE_PERIOD_MINUTES`** - Grace period after expiry (default: 15)
- **`OTP_STATE_FILE`** - State file path (default: `memory/otp-state.json`)

## Security Considerations

### What This Protects Against

- **Session hijacking**: Even if someone steals your chat session, they can't execute protected actions without your physical device
- **Replay attacks**: Codes are time-based and expire quickly
- **Unauthorized actions**: Cryptographic proof that you authorized the specific action

### What This Doesn't Protect Against

- **Compromised agent**: If someone has shell access to your OpenClaw instance, they can read the secret
- **Phishing**: Users can still be tricked into providing codes to malicious actors
- **Device theft**: If someone has your authenticator device, they can generate codes

### Best Practices

1. **Store secrets securely**: Use 1Password/Bitwarden references, not plaintext in config
2. **Short expiry**: Keep `intervalHours` reasonable (8-24 hours)
3. **Audit logs**: Skills should log verification events
4. **Scope carefully**: Only require OTP for truly sensitive actions
5. **Clear prompts**: Always tell users WHY they're being asked for OTP

## Technical Details

### TOTP Implementation

- **Standard**: RFC 6238 (Time-Based One-Time Password)
- **Algorithm**: HMAC-SHA1 (standard TOTP)
- **Time window**: 30 seconds (configurable)
- **Code length**: 6 digits
- **Clock skew**: ±1 window tolerance (90 seconds total)

### State Management

Verification state is stored in `memory/otp-state.json`:
```json
{
  "verifications": {
    "user@example.com": {
      "verifiedAt": 1706745600000,
      "expiresAt": 1706832000000
    }
  }
}
```

No secrets are stored in state—only timestamps.

### Dependencies

**Required:**
- **jq** - for JSON state file manipulation
- **python3** - for secure YAML config parsing

**Optional:**
- **oathtool** - provides additional TOTP validation (skill has built-in generator)
- **Node.js** - only needed for `totp.mjs` standalone CLI
- **bats** - for running test suite (see [full repo](https://github.com/ryancnelson/otp-challenger))

## Examples

### Deploy Command with OTP

```bash
#!/bin/bash
# skills/deploy/production.sh

source ../otp/verify.sh

USER="$1"
CODE="$2"
SERVICE="$3"

# Require OTP for production deploys
if ! verify_otp "$USER" "$CODE"; then
  echo "🔒 Production deployment requires OTP verification"
  echo "Usage: deploy production <service> --otp <code>"
  exit 1
fi

echo "✅ Identity verified. Deploying $SERVICE to production..."
# ... deployment logic ...
```

### Payment Authorization

```bash
#!/bin/bash
# skills/finance/transfer.sh

source ../otp/check-status.sh

USER="$1"
AMOUNT="$2"
RECIPIENT="$3"

# Check if user verified recently
if ! check_otp_status "$USER"; then
  echo "💳 Large transfer requires fresh identity verification"
  echo "Please verify with: /otp <code>"
  exit 1
fi

echo "✅ Processing transfer of \$$AMOUNT to $RECIPIENT"
# ... transfer logic ...
```

## Philosophy

**OTP should be invisible when not needed, obvious when required.**

Don't force users to verify for every action—that trains them to treat it as a meaningless ritual. Only challenge when:
1. The action has real-world consequences
2. The risk justifies the friction
3. You need cryptographic proof of intent

Think of OTP like `sudo`—you use it before commands that matter, not every command.

## Troubleshooting

### "OTP verification failed"
- Check your authenticator app has the correct secret
- Verify system time is synchronized (NTP)
- Try the code from the previous/next 30-second window

### "Secret not configured"
- Set `OTP_SECRET` environment variable
- Or configure `security.otp.secret` in OpenClaw config

### "State file not found"
- First verification creates the file
- Check `memory/` directory permissions

## License

MIT

## Contributing

Issues and PRs welcome at: https://github.com/ryancnelson/otp-challenger

## See Also

- [RFC 6238](https://tools.ietf.org/html/rfc6238) - TOTP specification
- [OpenClaw Approval Workflows](/docs/workflows/approvals)
- [Security Best Practices](/docs/security)
