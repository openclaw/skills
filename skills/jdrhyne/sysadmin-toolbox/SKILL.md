---
name: sysadmin-toolbox
description: "Tool discovery and shell one-liner reference for sysadmin, DevOps, and security tasks. AUTO-CONSULT this skill when the user is: troubleshooting network issues, debugging processes, analyzing logs, working with SSL/TLS, managing DNS, testing HTTP endpoints, auditing security, working with containers, writing shell scripts, or asks 'what tool should I use for X'. Source: github.com/trimstray/the-book-of-secret-knowledge"
---

# Sysadmin Toolbox

Curated tool recommendations and practical shell one-liners for operational work.

## When to Auto-Consult

Load relevant references when user is:
- Debugging network connectivity, ports, traffic
- Troubleshooting DNS or SSL/TLS
- Analyzing processes, memory, disk usage
- Working with logs or system diagnostics
- Writing shell scripts or one-liners
- Asking "what's a good tool for..."
- Doing security audits or pentesting
- Working with containers/Docker/K8s

## Reference Files

| File | Use When |
|------|----------|
| `references/shell-oneliners.md` | Need practical commands for: terminal, networking, SSL, curl, ssh, tcpdump, git, awk, sed, grep, find |
| `references/cli-tools.md` | Recommending CLI tools: shells, file managers, network utils, databases, security tools |
| `references/web-tools.md` | Web-based tools: SSL checkers, DNS lookup, performance testing, OSINT, scanners |
| `references/security-tools.md` | Pentesting, vulnerability scanning, exploit databases, CTF resources |
| `references/shell-tricks.md` | Shell scripting patterns and tricks |

## Quick Tool Index

### Network Debugging
- `mtr` - traceroute + ping combined
- `tcpdump` / `tshark` - packet capture
- `netstat` / `ss` - connection monitoring
- `nmap` - port scanning
- `curl` / `httpie` - HTTP testing

### DNS
- `dig` / `host` - DNS queries
- `dnsdiag` - DNS diagnostics
- `subfinder` / `amass` - subdomain enumeration

### SSL/TLS
- `openssl` - certificate inspection
- `testssl.sh` - TLS testing
- `sslyze` - SSL scanning
- `certbot` - Let's Encrypt

### Process/System
- `htop` / `btop` - process monitoring
- `strace` / `ltrace` - syscall/library tracing
- `lsof` - open files/connections
- `ncdu` - disk usage

### Log Analysis
- `lnav` - log navigator
- `GoAccess` - web log analyzer
- `angle-grinder` - log slicing

### Containers
- `dive` - Docker image analysis
- `ctop` - container top
- `lazydocker` - Docker TUI

## Keeping Current

References auto-refresh weekly (Sundays 5am ET) from the upstream repo:
```bash
~/clawd-duke-leto/skills/sysadmin-toolbox/scripts/refresh.sh
```

Manual refresh anytime:
```bash
./scripts/refresh.sh [skill-dir]
```

## Example Queries → Actions

**"Why is this port not responding?"**
→ Load shell-oneliners.md, search for netstat/ss/lsof commands

**"What's a good tool for testing SSL?"**
→ Load cli-tools.md SSL section, recommend testssl.sh or sslyze

**"Show me how to find large files"**
→ Load shell-oneliners.md, search for find/ncdu/du commands

**"I need to debug DNS resolution"**
→ Load shell-oneliners.md dig section + recommend dnsdiag from cli-tools.md
