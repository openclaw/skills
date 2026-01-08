---
name: clawdbot-skill-update
description: Comprehensive backup, update, and restore workflow with dynamic workspace detection
homepage: https://github.com/pasogott/clawdbot-skill-update
metadata: {"clawdbot":{"emoji":"💾","requires":{"bins":["bash","jq","tar","git"]},"tags":["backup","restore","update","multi-agent"]}}
---

# Clawdbot Update Skill

Comprehensive backup, update, and restore workflow for Clawdbot installations.

## Repository

- **GitHub**: https://github.com/clawdbot/clawdbot
- **Upstream**: `origin/main`
- **Local Clone**: `~/code/clawdbot` (default)

## Description

This skill provides a complete, **modular** update workflow for Clawdbot with **dynamic workspace detection**:
- Configuration files
- Agent states and sessions
- Credentials and auth tokens
- **All agent workspaces (auto-detected from config)**
- Cron jobs and sandboxes
- Git repository state

### Key Features

✅ **Dynamic Workspace Detection** - Reads workspace paths from config  
✅ **Multi-Agent Support** - Handles multiple agents automatically  
✅ **Safe Rollback** - Full restore capability  
✅ **Git Integration** - Tracks versions and remotes  
✅ **Validation** - Pre/post checks included  
✅ **Dry Run** - Preview before backup

## Files

- `config.json` - Skill configuration (repo URLs, paths)
- `backup-clawdbot-dryrun.sh` - **Dry run** preview (no changes)
- `backup-clawdbot-full.sh` - **Dynamic** full backup script
- `restore-clawdbot.sh` - **Dynamic** restore script
- `validate-setup.sh` - Pre/post update validation
- `check-upstream.sh` - Check for available updates
- `UPDATE_CHECKLIST.md` - Step-by-step update checklist
- `QUICK_REFERENCE.md` - Quick command reference
- `SKILL.md` - This file
- `README.md` - Quick start guide

### Dynamic Features

Both backup and restore scripts now:
- Read workspace paths from `~/.clawdbot/clawdbot.json`
- Support any number of agents
- Handle missing workspaces gracefully
- Generate safe filenames from agent IDs

## When to Use

Trigger this skill when asked to:
- "update clawdbot"
- "upgrade to latest version"
- "backup clawdbot before update"
- "restore clawdbot from backup"
- "rollback clawdbot update"

## Usage

### 1. Preview Backup (Dry Run)

```bash
~/.skills/clawdbot-update/backup-clawdbot-dryrun.sh
```

**Shows:**
- What files would be backed up
- Estimated backup size
- Workspace detection results
- Disk space availability
- Files that would be skipped

**No files are created or modified!**

### 2. Create Full Backup

```bash
~/.skills/clawdbot-update/backup-clawdbot-full.sh
```

**Backs up:**
- `~/.clawdbot/clawdbot.json` (config)
- `~/.clawdbot/sessions/` (session state)
- `~/.clawdbot/agents/` (multi-agent state)
- `~/.clawdbot/credentials/` (auth tokens)
- `~/.clawdbot/cron/` (scheduled jobs)
- `~/.clawdbot/sandboxes/` (sandbox state)
- All agent workspaces (dynamically detected!)
- Git commit and status

**Output:** `~/.clawdbot-backups/pre-update-YYYYMMDD-HHMMSS/`

### 3. Update Clawdbot

Follow the checklist:

```bash
cat ~/.skills/clawdbot-update/UPDATE_CHECKLIST.md
```

**Key steps:**
1. Create backup
2. Stop gateway
3. Pull latest code
4. Adjust config for breaking changes
5. Run doctor
6. Test functionality
7. Start gateway as daemon

### 4. Restore from Backup

```bash
~/.skills/clawdbot-update/restore-clawdbot.sh ~/.clawdbot-backups/pre-update-YYYYMMDD-HHMMSS
```

**Restores:**
- All configuration
- All state files
- All workspaces
- Optionally: git version

## Important Notes

### Multi-Agent Setup

This skill is designed for multi-agent setups with:
- Multiple agents with separate workspaces
- Sandbox configurations
- Provider routing (WhatsApp/Telegram/Discord/Slack/etc.)

### Breaking Changes in v2026.1.8

**CRITICAL:**
- **DM Lockdown**: DMs now default to `pairing` policy instead of open
- **Groups**: `telegram.groups` and `whatsapp.groups` are now allowlists
- **Sandbox**: Default scope changed to `"agent"` from implicit
- **Timestamps**: Now UTC format in agent envelopes

### Backup Validation

After backup, always verify:
```bash
BACKUP_DIR=~/.clawdbot-backups/pre-update-YYYYMMDD-HHMMSS
cat "$BACKUP_DIR/BACKUP_INFO.txt"
ls -lh "$BACKUP_DIR"
```

Should contain:
- ✅ `clawdbot.json`
- ✅ `credentials.tar.gz`
- ✅ `workspace-*.tar.gz` (one per agent)

### Config Changes Required

**Example: Switch WhatsApp to pairing:**
```bash
jq '.whatsapp.dmPolicy = "pairing"' ~/.clawdbot/clawdbot.json | sponge ~/.clawdbot/clawdbot.json
```

**Example: Set explicit sandbox scope:**
```bash
jq '.agent.sandbox.scope = "agent"' ~/.clawdbot/clawdbot.json | sponge ~/.clawdbot/clawdbot.json
```

## Workflow

### Standard Update Flow

```bash
# 1. Check for updates
~/.skills/clawdbot-update/check-upstream.sh

# 2. Validate current setup
~/.skills/clawdbot-update/validate-setup.sh

# 3. Dry run
~/.skills/clawdbot-update/backup-clawdbot-dryrun.sh

# 4. Backup
~/.skills/clawdbot-update/backup-clawdbot-full.sh

# 5. Stop gateway
cd ~/code/clawdbot
pnpm clawdbot gateway stop

# 6. Update code
git checkout main
git pull --rebase origin main
pnpm install
pnpm build

# 7. Run doctor
pnpm clawdbot doctor --yes

# 8. Test
pnpm clawdbot gateway start  # foreground for testing

# 9. Deploy
pnpm clawdbot gateway stop
pnpm clawdbot gateway start --daemon
```

### Rollback Flow

```bash
# Quick rollback
~/.skills/clawdbot-update/restore-clawdbot.sh <backup-dir>

# Manual rollback
cd ~/code/clawdbot
git checkout <old-commit>
pnpm install && pnpm build
cp <backup-dir>/clawdbot.json ~/.clawdbot/
pnpm clawdbot gateway restart
```

## Testing After Update

### Functionality Tests

- [ ] Provider DMs work (check pairing policy)
- [ ] Group mentions respond
- [ ] Typing indicators work
- [ ] Agent routing works
- [ ] Sandbox isolation works
- [ ] Tool restrictions enforced

### New Features
```bash
pnpm clawdbot agents list
pnpm clawdbot logs --tail 50
pnpm clawdbot providers list --usage
pnpm clawdbot skills list
```

### Monitoring

```bash
# Live logs
pnpm clawdbot logs --follow

# Or Web UI
open http://localhost:3001/logs

# Check status
pnpm clawdbot status
pnpm clawdbot gateway status
```

## Troubleshooting

### Common Issues

**Gateway won't start:**
```bash
pnpm clawdbot logs --grep error
pnpm clawdbot doctor
```

**Auth errors:**
```bash
# OAuth profiles might need re-login
pnpm clawdbot providers login <provider>
```

**Sandbox issues:**
```bash
# Check sandbox config
jq '.agent.sandbox' ~/.clawdbot/clawdbot.json

# Check per-agent sandbox
jq '.routing.agents[] | {name, sandbox}' ~/.clawdbot/clawdbot.json
```

### Emergency Restore

If something goes wrong:

```bash
# 1. Stop gateway
pnpm clawdbot gateway stop

# 2. Full restore
LATEST_BACKUP=$(ls -t ~/.clawdbot-backups/ | head -1)
~/.skills/clawdbot-update/restore-clawdbot.sh ~/.clawdbot-backups/$LATEST_BACKUP

# 3. Restart
pnpm clawdbot gateway start
```

## Installation

### Via ClawdHub

```bash
clawdbot skills install clawdbot-update
```

### Manual

```bash
git clone <repo-url> ~/.skills/clawdbot-update
chmod +x ~/.skills/clawdbot-update/*.sh
```

## License

MIT - see [LICENSE](LICENSE)

## Author

**Pascal Schott** ([@pasogott](https://github.com/pasogott))

Contribution for Clawdbot  
https://github.com/clawdbot/clawdbot
