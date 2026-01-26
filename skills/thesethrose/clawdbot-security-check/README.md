# Clawdbot Security Check

🔒 **Self-security audit framework for Clawdbot**

Inspired by the security hardening framework from [ᴅᴀɴɪᴇʟ ᴍɪᴇssʟᴇʀ](https://x.com/DanielMiessler) ([original post](https://x.com/DanielMiessler/status/2015865548714975475)).

This skill teaches Clawdbot to audit its own security posture using first-principles reasoning. Not a hard-coded script—it's a **knowledge framework** that Clawdbot applies dynamically to detect vulnerabilities, understand their impact, and recommend specific remediations.

## What This Is

- 🧠 **Knowledge-based** - Embeds the security framework directly in Clawdbot
- 🔍 **Dynamic detection** - Clawdbot learns to find issues, not just run a script
- 📚 **Extensible** - Add new checks by updating the skill
- 🔒 **100% Read-only** - Only audits; never modifies configuration

## The 10 Security Domains

| # | Domain | Severity | Key Question |
|---|--------|----------|--------------|
| 1 | Gateway Exposure | 🔴 Critical | Is the gateway bound to 0.0.0.0 without auth? |
| 2 | DM Policy | 🟠 High | Are DMs restricted to an allowlist? |
| 3 | Sandbox Isolation | 🟠 High | Is Docker sandbox enabled with network isolation? |
| 4 | Credentials Security | 🔴 Critical | Are secrets in plaintext with loose permissions? |
| 5 | Prompt Injection | 🟡 Medium | Is untrusted content wrapped to prevent injection? |
| 6 | Dangerous Commands | 🟠 High | Are destructive commands blocked? |
| 7 | Network Isolation | 🟡 Medium | Is Docker network restricted? |
| 8 | Elevated Tool Access | 🟡 Medium | Are tools restricted to minimum needed? |
| 9 | Audit Logging | 🟡 Medium | Is session activity logged for investigation? |
| 10| Pairing Codes | 🟡 Medium | Are codes cryptographic + rate-limited? |

## Installation

```bash
# Clone for Clawdbot skill integration
git clone https://github.com/TheSethRose/Clawdbot-Security-Check.git
cp -r Clawdbot-Security-Check ~/.clawdbot/skills/
```

## Usage

### Via Clawdbot
```
@clawdbot audit my security
@clawdbot run security check
@clawdbot what vulnerabilities do I have?
```

### Direct Execution
```bash
node security-check.js           # Human-readable report
node security-check.js --json    # JSON for programmatic use
```

## How It Works

Instead of a static script, this skill provides:

1. **Detection knowledge** - What config keys reveal each vulnerability
2. **Baseline definitions** - What "secure" looks like for each domain
3. **Remediation templates** - Specific fixes for each issue type
4. **Audit methodology** - Step-by-step execution framework

### Example: Clawdbot's Thought Process

When auditing, Clawdbot now thinks:

```
For Gateway Exposure:
1. Look at ~/.clawdbot/config.json for "bind_address"
2. If "0.0.0.0" AND no "auth_token" → VULNERABLE
3. Report: "Gateway exposed on 0.0.0.0:18789 without authentication"
4. Recommend: "Set gateway.auth_token in environment variables"
```

## Extending the Framework

Add new checks by contributing to SKILL.md:

```markdown
## 11. New Vulnerability 🟡 Medium

**What to check:** What config reveals this?

**How to detect:**
```bash
command-to-check-config
```

**Vulnerability:** What can go wrong?

**Remediation:**
```json
{
  "fix": "here"
}
```
```

## Architecture

```
Clawdbot-Security-Check/
├── SKILL.md          # Knowledge framework (the skill)
├── security-check.js # Reference implementation
├── README.md         # This file
├── package.json
└── .gitignore
```

**SKILL.md** is the source of truth—it teaches Clawdbot. **security-check.js** is a standalone reference implementation for CLI use.

## Why This Approach?

Hard-coded scripts get stale. A knowledge framework evolves:

- ✅ Add new vulnerabilities without code changes
- ✅ Customize checks for your environment
- ✅ Clawdbot understands the "why" behind each check
- ✅ Enables intelligent follow-up questions

> "The goal isn't to find vulnerabilities—it's to understand security deeply enough that vulnerabilities can't hide." — Daniel Miessler

## Output Example

```
═══════════════════════════════════════════════════════════════
🔒 CLAWDBOT SECURITY AUDIT
═══════════════════════════════════════════════════════════════
Timestamp: 2026-01-26T15:30:00.000Z

┌─ SUMMARY ───────────────────────────────────────────────
│ 🔴 Critical:  1
│ 🟠 High:      2
│ 🟡 Medium:    1
│ ✅ Passed:    6
└────────────────────────────────────────────────────────

┌─ FINDINGS ──────────────────────────────────────────────
│ 🔴 [CRITICAL] Gateway Exposure
│    Finding: Gateway bound to 0.0.0.0:18789 without auth
│    → Fix: Set gateway.auth_token environment variable
│
│ 🟠 [HIGH] DM Policy
│    Finding: dm_policy is "allow" (all users)
│    → Fix: Set dm_policy to "allowlist" with trusted users
└────────────────────────────────────────────────────────

This audit was performed by Clawdbot's self-security framework.
No changes were made to your configuration.
```

## Contributing

1. Fork the repo
2. Add new security knowledge to SKILL.md
3. Test with `node security-check.js`
4. Submit PR

## License

MIT - Security-first, open source forever.

---

**Clawdbot knows its attack surface. Do you?**
