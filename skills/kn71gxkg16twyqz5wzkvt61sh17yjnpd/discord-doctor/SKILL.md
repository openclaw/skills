---
name: discord-doctor
description: Quick diagnosis and repair for Discord bot, Gateway, OAuth token, and legacy config issues. Checks connectivity, token expiration, and cleans up old Clawdis artifacts.
metadata: {"clawdbot":{"emoji":"🩺","os":["darwin","linux"],"requires":{"bins":["node","curl"]}}}
---

# Discord Doctor

Quick diagnosis and repair for Discord/Gateway availability issues, OAuth token problems, and legacy Clawdis configuration conflicts.

## Usage

```bash
# Check status (diagnostic only)
discord-doctor

# Check and auto-fix issues
discord-doctor --fix
```

## What It Checks

1. **Discord App** - Is the Discord desktop app running (optional, for monitoring)
2. **Gateway Process** - Is the Clawdbot gateway daemon running
3. **Gateway HTTP** - Is the gateway responding on port 18789
4. **Discord Connection** - Is the bot actually connected to Discord (via `clawdbot health`)
5. **Anthropic OAuth** - Is your OAuth token valid or expired
6. **Legacy Clawdis** - Detects old launchd services and config directories that cause conflicts
7. **Recent Activity** - Shows recent Discord sessions

## Auto-Fix Capabilities

When run with `--fix`, it can:

- **Start gateway** if not running
- **Install missing npm packages** (like discord.js, strip-ansi)
- **Restart gateway** after fixing dependencies
- **Remove legacy launchd service** (`com.clawdis.gateway.plist`)
- **Backup legacy config** (moves `~/.clawdis` to `~/.clawdis-backup`)

## Common Issues & Fixes

| Issue | Auto-Fix Action |
|-------|-----------------|
| Gateway not running | Starts gateway on port 18789 |
| Missing npm packages | Runs `npm install` + installs specific package |
| Discord disconnected | Restarts gateway to reconnect |
| OAuth token expired | Shows instructions to re-authenticate |
| Legacy launchd service | Removes old `com.clawdis.gateway.plist` |
| Legacy ~/.clawdis config | Moves to `~/.clawdis-backup` |

## OAuth Token Issues

If you see "Access token EXPIRED", run:
```bash
cd ~/Clawdis && npx clawdbot configure
```
Then select "Anthropic OAuth (Claude Pro/Max)" to re-authenticate.

## Legacy Clawdis Migration

If you upgraded from Clawdis to Clawdbot, you may have legacy artifacts causing OAuth token conflicts:

- **Old launchd service**: `~/Library/LaunchAgents/com.clawdis.gateway.plist`
- **Old config directory**: `~/.clawdis/`

Run `discord-doctor --fix` to clean these up automatically.

## Example Output

```
Discord Doctor
Checking Discord and Gateway health...

1. Discord App
   Running (6 processes)

2. Gateway Process
   Running (PID: 66156, uptime: 07:45)

3. Gateway HTTP
   Responding on port 18789

4. Discord Connection
   Discord: ok (@Clawdis) (321ms)

5. Anthropic OAuth
   Valid (expires in 0h 45m)

6. Legacy Clawdis
   No legacy launchd service
   No legacy config directory

7. Recent Discord Activity
   - discord:group:123456789012345678 (21h ago)

Summary
All checks passed! Discord is healthy.
```
