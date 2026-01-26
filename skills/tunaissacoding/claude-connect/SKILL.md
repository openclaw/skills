---
name: claude-connect
description: "Connect Claude to Clawdbot instantly and keep it connected 24/7. Run after setup to link your subscription, then auto-refreshes tokens forever."
---

# claude-connect

**Connect your Claude subscription to Clawdbot in one step.**

Automatically:
- ✅ Reads Claude OAuth tokens from Keychain
- ✅ Writes them to Clawdbot in proper OAuth format
- ✅ Auto-refreshes every 2 hours (before expiry)
- ✅ Notifies you on success/failure
- ✅ Works with `clawdbot onboard` (fixes OAuth auth-profiles bug)

---

## Quick Start

**1. Install the skill:**
```bash
clawdhub install claude-connect
cd ~/clawd/skills/claude-connect
```

**2. Ensure Claude CLI is logged in:**
```bash
claude auth
# Follow the browser login flow
```

**3. Run installer:**
```bash
./install.sh
```

That's it! Tokens will refresh automatically every 2 hours.

---

## What It Does

### Fixes `clawdbot onboard` OAuth Bug

When you run `clawdbot onboard --auth-choice claude-cli`, it sometimes doesn't properly write OAuth tokens to `auth-profiles.json`.

This skill:
1. Reads OAuth tokens from macOS Keychain (where Claude CLI stores them)
2. Writes them to `~/.clawdbot/agents/main/agent/auth-profiles.json` in **proper OAuth format**:
   ```json
   {
     "profiles": {
       "anthropic:claude-cli": {
         "type": "oauth",
         "provider": "anthropic",
         "access": "sk-ant-...",
         "refresh": "sk-ant-ort...",
         "expires": 1234567890
       }
     }
   }
   ```
3. Sets up auto-refresh (runs every 2 hours via launchd)
4. Keeps your connection alive 24/7

---

## Installation

### Automatic (Recommended)

```bash
cd ~/clawd/skills/claude-connect
./install.sh
```

The installer will:
- ✅ Verify Claude CLI is set up
- ✅ Create config file
- ✅ Set up auto-refresh job (launchd)
- ✅ Run first refresh to test

### Manual

1. Copy example config:
   ```bash
   cp claude-oauth-refresh-config.example.json claude-oauth-refresh-config.json
   ```

2. Edit config (optional):
   ```bash
   nano claude-oauth-refresh-config.json
   ```

3. Test refresh:
   ```bash
   ./refresh-token.sh --force
   ```

4. Install launchd job (optional - for auto-refresh):
   ```bash
   cp com.clawdbot.claude-oauth-refresher.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.clawdbot.claude-oauth-refresher.plist
   ```

---

## Configuration

Edit `claude-oauth-refresh-config.json`:

```json
{
  "refresh_buffer_minutes": 30,
  "log_file": "~/clawd/logs/claude-oauth-refresh.log",
  "notifications": {
    "on_success": true,
    "on_failure": true
  },
  "notification_target": "YOUR_CHAT_ID"
}
```

**Options:**
- `refresh_buffer_minutes`: Refresh when token has this many minutes left (default: 30)
- `log_file`: Where to log refresh activity
- `notifications.on_success`: Notify on successful refresh (default: true)
- `notifications.on_failure`: Notify on failure (default: true)
- `notification_target`: Your Telegram chat ID (or leave empty to disable)

---

## Usage

### Manual Refresh

```bash
# Refresh now (even if not expired)
./refresh-token.sh --force

# Refresh only if needed
./refresh-token.sh
```

### Check Status

```bash
# View recent logs
tail ~/clawd/logs/claude-oauth-refresh.log

# Check auth profile
cat ~/.clawdbot/agents/main/agent/auth-profiles.json | jq '.profiles."anthropic:claude-cli"'

# Check Clawdbot status
clawdbot models status
```

### Disable Notifications

Ask Clawdbot:
```
Disable Claude refresh success notifications
```

Or edit config:
```json
{
  "notifications": {
    "on_success": false,
    "on_failure": true
  }
}
```

---

## How It Works

### Refresh Process

1. **Read from Keychain:** Gets OAuth tokens from `Claude Code-credentials`
2. **Check Expiry:** Only refreshes if < 30 minutes left (or `--force`)
3. **Call OAuth API:** Gets new access + refresh tokens
4. **Update auth-profiles.json:** Writes proper OAuth format
5. **Update Keychain:** Syncs new tokens back
6. **Restart Gateway:** Picks up new tokens
7. **Notify:** Sends success/failure message (optional)

### Auto-Refresh (launchd)

Runs every 2 hours via `~/Library/LaunchAgents/com.clawdbot.claude-oauth-refresher.plist`

**Controls:**
```bash
# Stop auto-refresh
launchctl unload ~/Library/LaunchAgents/com.clawdbot.claude-oauth-refresher.plist

# Start auto-refresh
launchctl load ~/Library/LaunchAgents/com.clawdbot.claude-oauth-refresher.plist

# Check if running
launchctl list | grep claude
```

---

## Troubleshooting

### OAuth not working after onboard

**Symptom:** `clawdbot onboard --auth-choice claude-cli` completes but Clawdbot can't use tokens

**Fix:**
```bash
cd ~/clawd/skills/claude-connect
./refresh-token.sh --force
```

This will write tokens in proper OAuth format.

### Tokens keep expiring

**Symptom:** Auth keeps failing after 8 hours

**Fix:** Ensure launchd job is running:
```bash
launchctl load ~/Library/LaunchAgents/com.clawdbot.claude-oauth-refresher.plist
launchctl list | grep claude
```

### No tokens in Keychain

**Symptom:** `No 'Claude Code-credentials' entries found`

**Fix:** Log in with Claude CLI:
```bash
claude auth
# Follow browser flow
```

Then run refresh again:
```bash
./refresh-token.sh --force
```

---

## Uninstall

```bash
cd ~/clawd/skills/claude-connect
./uninstall.sh
```

Or manually:
```bash
# Stop auto-refresh
launchctl unload ~/Library/LaunchAgents/com.clawdbot.claude-oauth-refresher.plist
rm ~/Library/LaunchAgents/com.clawdbot.claude-oauth-refresher.plist

# Remove skill
rm -rf ~/clawd/skills/claude-connect
```

---

## Upgrade

If you previously installed an older version:

```bash
cd ~/clawd/skills/claude-connect
./validate-update.sh  # Check what changed
clawdhub update claude-connect  # Update to latest
./install.sh  # Re-run installer if needed
```

---

## See Also

- [QUICKSTART.md](QUICKSTART.md) - 60-second setup guide
- [UPGRADE.md](UPGRADE.md) - Upgrading from older versions
- [Clawdbot docs](https://docs.clawd.bot) - Model authentication

---

**Version:** 1.1.0  
**Author:** TunaIssaCoding  
**License:** MIT  
**Repo:** https://github.com/TunaIssaCoding/claude-connect
