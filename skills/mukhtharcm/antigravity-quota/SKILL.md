---
name: antigravity-quota
version: 1.1.0
description: Check Antigravity account quotas for Claude and Gemini models. Shows remaining quota and reset times with ban detection.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":["node"]}}}
---

# Antigravity Quota Skill

Check quota status across all Antigravity accounts configured in Clawdbot.

## Prerequisites

- Clawdbot with Antigravity accounts configured
- Run `clawdbot configure` to add Antigravity accounts

## Quota Info

- **Claude (Opus/Sonnet)** — shared 5-hour quota pool
- **Gemini Pro** — separate 5-hour quota
- **Gemini Flash** — separate 5-hour quota

Each model type resets independently every 5 hours per account.

## Usage

### Text output (default)
```bash
node check-quota.js
```

### Markdown table (for tablesnap)
```bash
node check-quota.js --table
node check-quota.js --table | tablesnap --theme light -o /tmp/quota.png
```

### JSON output
```bash
node check-quota.js --json
```

### Custom timezone
```bash
node check-quota.js --tz America/New_York
TZ=Europe/London node check-quota.js
```

## Output

### Text mode
```
📊 Antigravity Quota Check - 2026-01-08T07:08:29.268Z
⏰ Each model type resets every 5 hours
🌍 Times shown in: Asia/Kolkata

Found 9 account(s)

🔍 user@gmail.com (project-abc123)
   claude-opus-4-5-thinking: 65.3% (resets 1:48 PM)
   gemini-3-flash: 95.0% (resets 11:41 AM)
```

### Table mode (`--table`)
Sorted by Claude quota remaining, with emoji indicators:
- 🟢 80%+ remaining
- 🟡 50-79% remaining  
- 🟠 20-49% remaining
- 🔴 <20% remaining

## Integration with tablesnap

For messaging platforms that don't render markdown tables:
```bash
node check-quota.js --table | tablesnap --theme light -o /tmp/quota.png
# Then send the image
```

Requires `tablesnap` — install with:
```bash
go install github.com/joargp/tablesnap/cmd/tablesnap@latest
```
