# Clawdbot Update - Quick Reference Card

## 🚀 One-Liner Commands

```bash
# Dry run (preview backup)
~/.skills/clawdbot-update/backup-clawdbot-dryrun.sh

# Backup everything
~/.skills/clawdbot-update/backup-clawdbot-full.sh

# Show checklist
cat ~/.skills/clawdbot-update/UPDATE_CHECKLIST.md

# Restore from backup
~/.skills/clawdbot-update/restore-clawdbot.sh <backup-dir>

# List backups
ls -lth ~/.clawdbot-backups/

# View last backup
cat $(ls -td ~/.clawdbot-backups/*/ | head -1)/BACKUP_INFO.txt
```

## ⚡ Emergency Rollback

```bash
# Stop gateway
cd ~/code/clawdbot && pnpm clawdbot gateway stop

# Restore latest backup
LATEST=$(ls -t ~/.clawdbot-backups/ | head -1)
~/.skills/clawdbot-update/restore-clawdbot.sh ~/.clawdbot-backups/$LATEST

# Start gateway
pnpm clawdbot gateway start
```

## 🔧 Config Quick Fixes

```bash
# Switch to pairing (recommended)
jq '.whatsapp.dmPolicy = "pairing" | .telegram.dmPolicy = "pairing"' ~/.clawdbot/clawdbot.json | sponge ~/.clawdbot/clawdbot.json

# Set explicit sandbox scope
jq '.agent.sandbox.scope = "agent"' ~/.clawdbot/clawdbot.json | sponge ~/.clawdbot/clawdbot.json

# Set user timezone
jq '.agent.userTimezone = "America/New_York"' ~/.clawdbot/clawdbot.json | sponge ~/.clawdbot/clawdbot.json

# View current config
jq '.' ~/.clawdbot/clawdbot.json | less
```

## 📊 Status Checks

```bash
# Gateway status
pnpm clawdbot gateway status

# Live logs
pnpm clawdbot logs --follow

# Agents
pnpm clawdbot agents list

# Providers with usage
pnpm clawdbot providers list --usage

# Full status
pnpm clawdbot status
```

## 🧪 Test Commands

```bash
# New CLIs
pnpm clawdbot agents list
pnpm clawdbot logs --tail 50
pnpm clawdbot providers list --usage
pnpm clawdbot skills list

# Web UI
open http://localhost:3001/logs

# Check routing
jq '.routing.bindings' ~/.clawdbot/clawdbot.json
```

## 🎯 Critical Checks

```bash
# DM policies
jq '.whatsapp.dmPolicy, .telegram.dmPolicy' ~/.clawdbot/clawdbot.json

# Groups config
jq '.telegram.groups, .whatsapp.groups' ~/.clawdbot/clawdbot.json

# Sandbox config
jq '.agent.sandbox' ~/.clawdbot/clawdbot.json

# Per-agent config
jq '.routing.agents[] | {name, workspace, sandbox}' ~/.clawdbot/clawdbot.json

# Workspaces list
jq -r '.routing.agents | to_entries[] | "\(.key): \(.value.workspace)"' ~/.clawdbot/clawdbot.json
```

## 🔥 Troubleshooting

```bash
# Logs with errors
pnpm clawdbot logs --grep error

# Run doctor
pnpm clawdbot doctor --yes

# Restart gateway
pnpm clawdbot gateway restart

# Kill stuck processes
pkill -f "clawdbot gateway"

# Check gateway ports
lsof -i :3001 -i :3002
```

## 📦 Update Flow (Copy-Paste)

```bash
# 0. Dry run (optional)
~/.skills/clawdbot-update/backup-clawdbot-dryrun.sh

# 1. Backup
~/.skills/clawdbot-update/backup-clawdbot-full.sh

# 2. Stop
cd ~/code/clawdbot && pnpm clawdbot gateway stop

# 3. Update
git checkout main
git pull --rebase origin main
pnpm install
pnpm build

# 4. Config (adjust as needed)
jq '.whatsapp.dmPolicy = "pairing"' ~/.clawdbot/clawdbot.json | sponge ~/.clawdbot/clawdbot.json
jq '.agent.sandbox.scope = "agent"' ~/.clawdbot/clawdbot.json | sponge ~/.clawdbot/clawdbot.json

# 5. Doctor
pnpm clawdbot doctor --yes

# 6. Start
pnpm clawdbot gateway start --daemon

# 7. Verify
pnpm clawdbot gateway status
pnpm clawdbot logs --tail 20
```

## 🎓 Version Check

```bash
# Current version
cd ~/code/clawdbot && git log -1 --oneline

# Upstream version
git fetch origin && git log main..origin/main --oneline | head -5

# Check for updates
git fetch origin && git diff --stat main..origin/main
```

## 💾 Workspace Checks

```bash
# List configured workspaces
jq -r '.routing.agents | to_entries[] | "\(.key): \(.value.workspace)"' ~/.clawdbot/clawdbot.json

# Check workspace sizes
du -sh ~/clawd*

# Check .clawdbot size
du -sh ~/.clawdbot

# Backup size
du -sh ~/.clawdbot-backups/
```

## 🔐 Auth Check

```bash
# List credentials
ls -la ~/.clawdbot/credentials/

# Check auth profiles
jq '.models' ~/.clawdbot/clawdbot.json

# Provider login status
pnpm clawdbot providers list
```

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Backup | 2-3 min |
| Update code | 3-5 min |
| Config changes | 5-10 min |
| Doctor | 2-3 min |
| Testing | 10-15 min |
| **Total** | **25-35 min** |

## 📞 Emergency Contacts

**Logs:** `~/.clawdbot/logs/`  
**Backups:** `~/.clawdbot-backups/`  
**Config:** `~/.clawdbot/clawdbot.json`  
**Skill:** `~/.skills/clawdbot-update/`

---

**Last Updated:** 2026-01-08  
**Target Version:** v2026.1.8  
**Repository:** https://github.com/clawdbot/clawdbot
