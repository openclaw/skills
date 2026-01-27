---
name: fail2ban-reporter
description: "Auto-report fail2ban banned IPs to AbuseIPDB and notify via Telegram. Use when monitoring server security, reporting attackers, or checking banned IPs. Watches fail2ban for new bans, reports them to AbuseIPDB, and sends alerts."
---

# fail2ban Reporter

Monitor fail2ban bans and auto-report attackers to AbuseIPDB.

## Setup

1. Get a free AbuseIPDB API key at https://www.abuseipdb.com/account/api
2. Store it: `pass insert abuseipdb/api-key`
3. Install the monitor: `bash {baseDir}/scripts/install.sh`

## Manual Usage

### Report all currently banned IPs

```bash
bash {baseDir}/scripts/report-banned.sh
```

### Check a specific IP

```bash
bash {baseDir}/scripts/check-ip.sh <ip>
```

### Show ban stats

```bash
bash {baseDir}/scripts/stats.sh
```

## Auto-Reporting

The install script sets up a fail2ban action that auto-reports new bans.

```bash
bash {baseDir}/scripts/install.sh    # install auto-reporting
bash {baseDir}/scripts/uninstall.sh  # remove auto-reporting
```

## Heartbeat Integration

Add to HEARTBEAT.md to check for new bans periodically:

```markdown
- [ ] Check fail2ban stats and report any unreported IPs to AbuseIPDB
```

## Workflow

1. fail2ban bans an IP → action triggers `report-single.sh`
2. Script reports to AbuseIPDB with SSH brute-force category
3. Sends Telegram notification (if configured)
4. Logs report to `/var/log/abuseipdb-reports.log`

## API Reference

See [references/abuseipdb-api.md](references/abuseipdb-api.md) for full API docs.
