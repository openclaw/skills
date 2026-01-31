# OTP Identity Challenge - OpenClaw Skill

**Identity verification for approval workflows in OpenClaw.**

This skill enables agents to challenge users for fresh two-factor authentication proof before executing sensitive actions—deployments, financial operations, data access, or any command with change-control concerns.

## Quick Start

```bash
# Install via ClawHub
clawhub install otp

# Or clone manually
cd ~/.openclaw/skills
git clone https://github.com/ryancnelson/otp-skill.git otp
```

## Purpose

This is **not** chat channel security—it's **identity verification for specific actions**.

When your agent needs to execute something sensitive, it challenges the user to prove their identity with a time-based one-time password (TOTP), providing cryptographic proof they authorized the action.

## Example

```bash
#!/bin/bash
# In your deploy skill

source ../otp/verify.sh

if ! verify_otp "$USER" "$OTP_CODE"; then
  echo "🔒 Production deployment requires OTP verification"
  exit 1
fi

echo "✅ Identity verified. Deploying..."
kubectl apply -f production.yaml
```

## Documentation

See **[SKILL.md](./SKILL.md)** for complete documentation:
- Installation & setup
- Usage examples
- Security considerations
- Configuration options
- Troubleshooting

## Philosophy

**OTP should be invisible when not needed, obvious when required.**

Only challenge when the action has real consequences. Think of it like `sudo` for your AI agent—use it before commands that matter.

## Full Source & Tests

For the complete repository with git history, test suite, and development files:
**https://github.com/ryancnelson/otp-challenger**

## License

MIT

## Author

Ryan Nelson
