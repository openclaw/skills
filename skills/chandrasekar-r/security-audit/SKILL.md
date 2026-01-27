---
name: security-audit
description: Comprehensive security auditing for Clawdbot deployments. Scans for exposed credentials, open ports, weak configs, and vulnerabilities. Auto-fix mode included.
---

# Security Audit Skill

## When to use

Run a security audit to identify vulnerabilities in your Clawdbot setup before deployment or on a schedule. Use auto-fix to remediate common issues automatically.

## Setup

No external dependencies required. Uses native system tools where available.

## How to

### Quick audit (common issues)

```bash
node skills/security-audit/scripts/audit.cjs
```

### Full audit (comprehensive scan)

```bash
node skills/security-audit/scripts/audit.cjs --full
```

### Auto-fix common issues

```bash
node skills/security-audit/scripts/audit.cjs --fix
```

### Audit specific areas

```bash
node skills/security-audit/scripts/audit.cjs --credentials      # Check for exposed API keys
node skills/security-audit/scripts/audit.cjs --ports            # Scan for open ports
node skills/security-audit/scripts/audit.cjs --configs          # Validate configuration
node skills/security-audit/scripts/audit.cjs --permissions      # Check file permissions
node skills/security-audit/scripts/audit.cjs --docker           # Docker security checks
```

### Generate report

```bash
node skills/security-audit/scripts/audit.cjs --full --json > audit-report.json
```

## Output

The audit produces a report with:

| Level | Description |
|-------|-------------|
| 🔴 CRITICAL | Immediate action required (exposed credentials) |
| 🟠 HIGH | Significant risk, fix soon |
| 🟡 MEDIUM | Moderate concern |
| 🟢 INFO | FYI, no action needed |

## Checks Performed

### Credentials
- API keys in environment files
- Tokens in command history
- Hardcoded secrets in code
- Weak password patterns

### Ports
- Unexpected open ports
- Services exposed to internet
- Missing firewall rules

### Configs
- Missing rate limiting
- Disabled authentication
- Default credentials
- Open CORS policies

### Files
- World-readable files
- Executable by anyone
- Sensitive files in public dirs

### Docker
- Privileged containers
- Missing resource limits
- Root user in container

## Auto-Fix

The `--fix` option automatically:
- Sets restrictive file permissions (600 on .env)
- Secures sensitive configuration files
- Creates .gitignore if missing
- Enables basic security headers

## Related skills

- `security-monitor` - Real-time monitoring (available separately)
