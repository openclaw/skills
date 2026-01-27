# 🛡️ Clawdbot fail2ban Reporter

Auto-report fail2ban banned IPs to [AbuseIPDB](https://www.abuseipdb.com), protecting the community from brute-force attackers.

Built for [Clawdbot](https://github.com/clawdbot/clawdbot) — works as a standalone tool too.

## Why?

Every server with a public IP gets attacked. fail2ban blocks them locally — but reporting to AbuseIPDB blocks them **globally**. When you report an attacker, every other server using AbuseIPDB's blocklist benefits.

Real stats from a fresh server:

```
Within 60 seconds of enabling fail2ban:
→ 62 failed SSH attempts
→ 9 unique IPs banned  
→ Attacks from 7 countries
```

## Quick Start

### 1. Get an AbuseIPDB API Key (free)

Sign up at [abuseipdb.com](https://www.abuseipdb.com/account/api) — free tier allows 1000 reports/day.

### 2. Store your API key

```bash
# Using pass (recommended)
pass insert abuseipdb/api-key

# Or export directly
export ABUSEIPDB_KEY="your-api-key"
```

### 3. Report currently banned IPs

```bash
bash scripts/report-banned.sh
```

### 4. Enable auto-reporting (optional)

```bash
sudo bash scripts/install.sh
```

Now every new fail2ban ban automatically reports to AbuseIPDB.

## Usage

### Report all banned IPs
```bash
bash scripts/report-banned.sh          # default: sshd jail
bash scripts/report-banned.sh nginx    # custom jail
```

### Check an IP's reputation
```bash
bash scripts/check-ip.sh 1.2.3.4
```

### View stats
```bash
bash scripts/stats.sh
```

### Remove auto-reporting
```bash
sudo bash scripts/uninstall.sh
```

## Clawdbot Skill

If you're using Clawdbot, install as a skill:

```bash
# Copy to skills directory
cp -r . ~/.clawdbot/skills/fail2ban-reporter/
```

Then ask your Clawdbot:
- "Report banned IPs to AbuseIPDB"
- "Check IP 1.2.3.4"
- "Show fail2ban stats"

### Heartbeat Integration

Add to your `HEARTBEAT.md`:

```markdown
- [ ] Check fail2ban for new bans, report unreported IPs to AbuseIPDB
```

## How It Works

```
Attacker → SSH brute-force → fail2ban bans IP → report-single.sh
                                                      ↓
                                              AbuseIPDB API (report)
                                                      ↓
                                              /var/log/abuseipdb-reports.log
```

## Prerequisites

- `fail2ban` — `sudo apt install fail2ban`
- `jq` — `sudo apt install jq`
- `curl` — usually pre-installed
- `pass` (optional) — for secure API key storage

## License

MIT — report those attackers, protect the community! 🛡️
