---
name: sec-filing-watcher
description: Monitor SEC EDGAR for new filings and get Telegram/Slack summaries via Clawdbot. Use when setting up SEC filing alerts, adding/removing tickers to monitor, configuring form types, starting/stopping the watcher, or troubleshooting filing notifications.
---

# SEC Filing Watcher

Monitors SEC EDGAR for new filings from a watchlist of tickers. When a new filing appears, notifies Clawdbot which fetches, summarizes, and sends to Telegram.

## Quick Setup

### 1. Create watchlist

```bash
cp assets/watchlist.example.json watchlist.json
# Edit watchlist.json with your tickers
```

### 2. Configure webhook

Edit `scripts/watcher.js` CONFIG section:
- `webhookUrl`: Your Clawdbot hooks URL (default: `http://localhost:18789/hooks/agent`)
- `webhookToken`: Your hook token (find in clawdbot.json under `hooks.token`)

### 3. Test run

```bash
node scripts/watcher.js
```

First run seeds existing filings (no notifications). Second run checks for new filings.

### 4. Schedule (every 15 min)

**macOS:**
```bash
cp assets/com.sec-watcher.plist ~/Library/LaunchAgents/
# Edit the plist to set correct paths
launchctl load ~/Library/LaunchAgents/com.sec-watcher.plist
```

**Linux:**
```bash
crontab -e
# Add: */15 * * * * /usr/bin/node /path/to/scripts/watcher.js >> /path/to/watcher.log 2>&1
```

## Managing Tickers

Add or remove tickers in `watchlist.json`:

```json
{
  "tickers": ["AAPL", "MSFT", "TSLA"],
  "formTypes": ["10-K", "10-Q", "8-K", "4"]
}
```

New tickers are auto-seeded (existing filings won't spam you).

See `references/form-types.md` for common SEC form types.

## Commands

**Check status:**
```bash
launchctl list | grep sec-watcher
```

**View logs:**
```bash
cat ~/clawd/sec-filing-watcher/watcher.log
```

**Stop:**
```bash
launchctl unload ~/Library/LaunchAgents/com.sec-watcher.plist
```

**Start:**
```bash
launchctl load ~/Library/LaunchAgents/com.sec-watcher.plist
```

**Manual run:**
```bash
node scripts/watcher.js
```

## Files

| File | Purpose |
|------|---------|
| `scripts/watcher.js` | Main watcher script |
| `watchlist.json` | Your tickers and form types |
| `state.json` | Tracks seen filings (auto-created) |
| `watcher.log` | Output log (if configured) |

## Troubleshooting

**No notifications:**
- Check `state.json` exists (first run seeds, second run notifies)
- Verify webhook URL and token in watcher.js CONFIG
- Check Clawdbot is running: `clawdbot status`

**SEC blocking requests:**
- Script uses proper User-Agent header
- If blocked, wait 10 minutes (SEC rate limit cooldown)

**Duplicate notifications:**
- Check `state.json` isn't corrupted
- Delete `state.json` to re-seed (will seed all existing filings again)
