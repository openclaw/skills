---
name: security-monitor
description: Real-time security monitoring for Clawdbot. Detects intrusions, unusual API calls, credential usage patterns, and alerts on breaches.
---

# Security Monitor Skill

## When to use

Run continuous security monitoring to detect breaches, intrusions, and unusual activity on your Clawdbot deployment.

## Setup

No external dependencies required. Runs as a background process.

## How to

### Start real-time monitoring

```bash
node skills/security-monitor/scripts/monitor.cjs --interval 60
```

### Run in daemon mode (background)

```bash
node skills/security-monitor/scripts/monitor.cjs --daemon --interval 60
```

### Monitor for specific threats

```bash
node skills/security-monitor/scripts/monitor.cjs --threats=credentials,ports,api-calls
```

## What It Monitors

| Threat | Detection | Response |
|--------|-----------|----------|
| **Brute force attacks** | Failed login detection | Alert + IP tracking |
| **Port scanning** | Rapid connection attempts | Alert |
| **Process anomalies** | Unexpected processes | Alert |
| **File changes** | Unauthorized modifications | Alert |
| **Container health** | Docker issues | Alert |

## Output

- Console output (stdout)
- JSON logs at `/root/clawd/clawdbot-security/logs/alerts.log`
- Telegram alerts (configurable)

## Daemon Mode

Use systemd or PM2 to keep monitoring active:

```bash
# With PM2
pm2 start monitor.cjs --name "clawdbot-security" -- --daemon --interval 60
```

## Combined with Security Audit

Run audit first, then monitor continuously:

```bash
# One-time audit
node skills/security-audit/scripts/audit.cjs --full

# Continuous monitoring
node skills/security-monitor/scripts/monitor.cjs --daemon
```

## Related skills

- `security-audit` - One-time security scan (install separately)
