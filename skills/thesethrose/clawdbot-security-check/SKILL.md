---
name: clawdbot-self-security-audit
description: Perform a comprehensive read-only security audit of Clawdbot's own configuration. This is a knowledge-based skill that teaches Clawdbot to identify hardening opportunities across the system. Use when user asks to "run security check", "audit clawdbot", "check security hardening", or "what vulnerabilities does my Clawdbot have". This skill uses Clawdbot's internal capabilities and file system access to inspect configuration, detect misconfigurations, and recommend remediations. It is designed to be extensible - new checks can be added by updating this skill's knowledge.
homepage: https://github.com/TheSethRose/Clawdbot-Security-Check
metadata: {"clawdbot":{"emoji":"🔒","os":["darwin","linux"],"requires":{"files":["read"],"tools":["exec","bash"]},"install":[{"id":"read-skill","kind":"skill","name":"clawdbot-self-security-audit","label":"Install security audit skill","bins":["SKILL.md"]}]}}
---

# Clawdbot Self-Security Audit Framework

This skill empowers Clawdbot to audit its own security posture using first-principles reasoning. Rather than relying on a static script, Clawdbot learns the framework and applies it dynamically to detect vulnerabilities, understand their impact, and recommend specific remediations.

## Core Philosophy

> "Security through transparency and self-awareness." — Inspired by ᴅᴀɴɪᴇʟ ᴍɪᴇssʟᴇʀ

Clawdbot should know its own attack surface. This skill embeds that knowledge directly.

## The 10 Security Domains

When auditing Clawdbot, systematically evaluate these domains:

### 1. Gateway Exposure 🔴 Critical

**What to check:**
- Where is the gateway binding? (`gateway.bind_address`)
- Is authentication configured? (`gateway.auth_token` or `CLAWDBOT_AUTH_TOKEN` env var)
- What port is exposed? (default: 18789)

**How to detect:**
```bash
# Check current binding
cat ~/.clawdbot/config.json | grep -A5 '"gateway"'
echo "AUTH_TOKEN set: $(env | grep CLAWDBOT_AUTH_TOKEN | wc -l)"
```

**Vulnerability:** Binding to `0.0.0.0` without auth allows anyone on the network to control Clawdbot.

**Remediation:**
```bash
export CLAWDBOT_AUTH_TOKEN="$(openssl rand -hex 32)"
```

---

### 2. DM Policy Configuration 🟠 High

**What to check:**
- What is `dm_policy` set to?
- If `allowlist`, who is explicitly allowed via `dm_policy_allowlist`?

**How to detect:**
```bash
cat ~/.clawdbot/config.json | grep -E '"dm_policy|"dm_policy_allowlist"'
```

**Vulnerability:** Setting to `allow` or `all` means any user can DM Clawdbot and potentially exploit vulnerabilities.

**Remediation:**
```json
{
  "dm_policy": "allowlist",
  "dm_policy_allowlist": ["@trusteduser1", "@trusteduser2"]
}
```

---

### 3. Sandbox Isolation 🟠 High

**What to check:**
- Is `sandbox` enabled? (`all`, `disabled`, `false`)
- Is Docker network isolated? (`docker.network`)

**How to detect:**
```bash
cat ~/.clawdbot/config.json | grep -A3 '"sandbox"|"docker"'
```

**Vulnerability:** Disabled sandbox allows tool execution to escape containment, potentially compromising the host.

**Remediation:**
```json
{
  "sandbox": "all",
  "docker": {
    "network": "none"
  }
}
```

---

### 4. Credentials Security 🔴 Critical

**What to check:**
- Does `~/.clawdbot/oauth.json` exist?
- What are its file permissions?
- Are credentials stored in environment variables?

**How to detect:**
```bash
ls -la ~/.clawdbot/oauth.json 2>/dev/null
stat -c "%a" ~/.clawdbot/oauth.json 2>/dev/null
env | grep -E "OAUTH|TOKEN|SECRET" | wc -l
```

**Vulnerability:** Plaintext credentials with loose permissions can be read by any process.

**Remediation:**
```bash
chmod 600 ~/.clawdbot/oauth.json
# Use env vars for all sensitive values
export CLAWDBOT_OAUTH_TOKEN="..."
```

---

### 5. Prompt Injection Protection 🟡 Medium

**What to check:**
- Is `wrap_untrusted_content` or `untrusted_content_wrapper` enabled?
- How is external/web content handled?

**How to detect:**
```bash
cat ~/.clawdbot/config.json | grep -i "untrusted|wrap"
```

**Vulnerability:** Untrusted content (web fetches, sandbox output) can inject malicious prompts that override Clawdbot's instructions.

**Remediation:**
```json
{
  "wrap_untrusted_content": true,
  "untrusted_content_wrapper": "<untrusted>"
}
```

---

### 6. Dangerous Command Blocking 🟠 High

**What to check:**
- What commands are in `blocked_commands` or `dangerous_commands`?
- Are these patterns included: `rm -rf`, `curl |`, `git push --force`, `mkfs`, fork bombs?

**How to detect:**
```bash
cat ~/.clawdbot/config.json | grep -A10 '"blocked_commands"'
```

**Vulnerability:** Without blocking, a malicious prompt could destroy data or exfiltrate credentials.

**Remediation:**
```json
{
  "blocked_commands": [
    "rm -rf",
    "curl |",
    "git push --force",
    "mkfs",
    ":(){:|:&}",
    "wget",
    "nc ",
    "exec "
  ]
}
```

---

### 7. Network Isolation 🟡 Medium

**What to check:**
- What is `docker.network` set to?
- Is Clawdbot's Docker container network-restricted?

**How to detect:**
```bash
cat ~/.clawdbot/config.json | grep -A2 '"docker"'
docker network ls 2>/dev/null | grep -v "bridge\|host\|none"
```

**Vulnerability:** Default Docker networking allows containers to reach the LAN and potentially pivot attacks.

**Remediation:**
```json
{
  "docker": {
    "network": "none"
  }
}
```
Or use a custom isolated network.

---

### 8. Elevated Tool Access 🟡 Medium

**What to check:**
- Is `restrict_tools` or `mcp_tools.restrict` enabled?
- Which tools have elevated permissions?

**How to detect:**
```bash
cat ~/.clawdbot/config.json | grep -i "restrict|mcp"
cat ~/.clawdbot/config.json | grep -A50 '"mcp_tools"'
```

**Vulnerability:** Broad tool access means more blast radius if Clawdbot is compromised.

**Remediation:**
```json
{
  "restrict_tools": true,
  "mcp_tools": {
    "allowed": ["read", "write", "bash"],
    "blocked": ["exec", "gateway"]
  }
}
```

---

### 9. Audit Logging 🟡 Medium

**What to check:**
- Is `audit_logging`, `session_logging`, or `audit` enabled?
- Where are logs written?

**How to detect:**
```bash
cat ~/.clawdbot/config.json | grep -i "audit|session_log"
ls -la ~/.clawdbot/logs/ 2>/dev/null
```

**Vulnerability:** Without logging, there's no evidence trail for incident investigation.

**Remediation:**
```json
{
  "audit_logging": true,
  "session_logging": {
    "path": "~/.clawdbot/logs/",
    "retention_days": 90
  }
}
```

---

### 10. Pairing Code Security 🟡 Medium

**What to check:**
- What is `pairing.code_length`?
- Is `rate_limit` or `max_attempts` configured?

**How to detect:**
```bash
cat ~/.clawdbot/config.json | grep -A5 '"pairing"'
```

**Vulnerability:** Short codes with no rate limiting are vulnerable to brute-force attacks.

**Remediation:**
```json
{
  "pairing": {
    "code_length": 12,
    "rate_limit": {
      "max_attempts": 5,
      "lockout_minutes": 30
    }
  }
}
```

## Audit Execution Steps

When running a security audit, follow this sequence:

### Step 1: Locate Configuration
```bash
CONFIG_PATHS=(
  "$HOME/.clawdbot/config.json"
  "$HOME/.clawdbot/config.yaml"
  "$HOME/.clawdbot/.clawdbotrc"
  ".clawdbotrc"
)
for path in "${CONFIG_PATHS[@]}"; do
  if [ -f "$path" ]; then
    echo "Found config: $path"
    cat "$path"
    break
  fi
done
```

### Step 2: Run Domain Checks
For each of the 10 domains above:
1. Parse relevant config keys
2. Compare against secure baseline
3. Flag deviations with severity

### Step 3: Generate Report
Format findings by severity:
```
🔴 CRITICAL: [vulnerability] - [impact]
🟠 HIGH: [vulnerability] - [impact]
🟡 MEDIUM: [vulnerability] - [impact]
✅ PASSED: [check name]
```

### Step 4: Provide Remediation
For each finding, output:
- Specific config change needed
- Example configuration
- Command to apply (if safe)

## Report Template

```
═══════════════════════════════════════════════════════════════
🔒 CLAWDBOT SECURITY AUDIT
═══════════════════════════════════════════════════════════════
Timestamp: $(date -Iseconds)

┌─ SUMMARY ───────────────────────────────────────────────
│ 🔴 Critical:  $CRITICAL_COUNT
│ 🟠 High:      $HIGH_COUNT
│ 🟡 Medium:    $MEDIUM_COUNT
│ ✅ Passed:    $PASSED_COUNT
└────────────────────────────────────────────────────────

┌─ FINDINGS ──────────────────────────────────────────────
│ 🔴 [CRITICAL] $VULN_NAME
│    Finding: $DESCRIPTION
│    → Fix: $REMEDIATION
│
│ 🟠 [HIGH] $VULN_NAME
│    ...
└────────────────────────────────────────────────────────

This audit was performed by Clawdbot's self-security framework.
No changes were made to your configuration.
```

## Extending the Skill

To add new security checks:

1. **Identify the vulnerability** - What misconfiguration creates risk?
2. **Determine detection method** - What config key or system state reveals it?
3. **Define the baseline** - What is the secure configuration?
4. **Write detection logic** - Shell commands or file parsing
5. **Document remediation** - Specific steps to fix
6. **Assign severity** - Critical, High, Medium, Low

### Example: Adding SSH Hardening Check

```
## 11. SSH Agent Forwarding 🟡 Medium

**What to check:** Is SSH_AUTH_SOCK exposed to containers?

**Detection:**
```bash
env | grep SSH_AUTH_SOCK
```

**Vulnerability:** Container escape via SSH agent hijacking.

**Severity:** Medium
```

## Security Assessment Questions

When auditing, ask:

1. **Exposure:** What network interfaces can reach Clawdbot?
2. **Authentication:** What验证验证 does each access point require?
3. **Isolation:** What boundaries exist between Clawdbot and the host?
4. **Trust:** What content sources are considered "trusted"?
5. **Auditability:** What evidence exists of Clawdbot's actions?
6. **Least Privilege:** Does Clawdbot have only necessary permissions?

## Principles Applied

- **Zero modification** - This skill only reads; it never changes configuration
- **Defense in depth** - Multiple checks catch different attack vectors
- **Actionable output** - Every finding includes a concrete remediation
- **Extensible design** - New checks integrate naturally

## References

- Original framework: [ᴅᴀɴɪᴇʟ ᴍɪᴇssʟᴇʀ on X](https://x.com/DanielMiessler/status/2015865548714975475)
- Repository: https://github.com/TheSethRose/Clawdbot-Security-Check

---

**Remember:** This skill exists to make Clawdbot self-aware of its security posture. Use it regularly, extend it as needed, and never skip the audit.
