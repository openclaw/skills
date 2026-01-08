# Clawdbot Update to v2026.1.8 - Checklist

## ✅ Pre-Update Checklist

- [ ] **Backup created**: `/tmp/backup-clawdbot-full.sh`
- [ ] **Gateway stopped**: `pnpm clawdbot gateway stop`
- [ ] **Backup validated**: All important files present
- [ ] **Time window**: 45-60 minutes planned

## 📦 Backup Locations

```bash
# Backup Script
~/.skills/clawdbot-update/backup-clawdbot-full.sh

# Restore Script
~/.skills/clawdbot-update/restore-clawdbot.sh

# Backup will be saved in:
~/.clawdbot-backups/pre-update-YYYYMMDD-HHMMSS/
```

## 🚀 Update Steps

### 1. Backup (10 min)
```bash
~/.skills/clawdbot-update/backup-clawdbot-dryrun.sh  # Dry run first
~/.skills/clawdbot-update/backup-clawdbot-full.sh
```

### 2. Update Code (5 min)
```bash
cd ~/code/clawdbot  # Or your clawdbot path
git checkout main
git pull --rebase origin main
pnpm install
pnpm build
```

### 3. Config Adjustments (10 min)

#### A) WhatsApp/Telegram dmPolicy (CRITICAL!)
```bash
# Check current policy
jq '.whatsapp.dmPolicy, .telegram.dmPolicy' ~/.clawdbot/clawdbot.json

# Option 1: Use pairing (recommended for security)
jq '.whatsapp.dmPolicy = "pairing" | .telegram.dmPolicy = "pairing"' ~/.clawdbot/clawdbot.json > /tmp/temp.json
mv /tmp/temp.json ~/.clawdbot/clawdbot.json

# Option 2: Keep allowlist (verify your allowFrom list!)
jq '.whatsapp.allowFrom, .telegram.allowFrom' ~/.clawdbot/clawdbot.json
```

#### B) Sandbox Scope (set explicitly)
```bash
jq '.agent.sandbox.scope = "agent"' ~/.clawdbot/clawdbot.json > /tmp/temp.json
mv /tmp/temp.json ~/.clawdbot/clawdbot.json
```

#### C) User Timezone (optional)
```bash
# Set your timezone for better timestamps
jq '.agent.userTimezone = "America/New_York"' ~/.clawdbot/clawdbot.json > /tmp/temp.json
mv /tmp/temp.json ~/.clawdbot/clawdbot.json
```

### 4. Doctor (5 min)
```bash
cd ~/code/clawdbot
pnpm clawdbot gateway start  # Foreground
# New terminal:
pnpm clawdbot doctor --yes
```

### 5. Tests (10 min)

#### Provider Tests
- [ ] Test DM to bot → Works with pairing
- [ ] Test group mentions → Bot responds
- [ ] Test media upload → Works

#### Multi-Agent (if configured)
- [ ] Agent routing works correctly
- [ ] Sandbox isolation works
- [ ] Tool restrictions work

#### New Features
- [ ] `pnpm clawdbot agents list`
- [ ] `pnpm clawdbot logs --tail 50`
- [ ] `pnpm clawdbot providers list --usage`
- [ ] Web UI Logs Tab: http://localhost:3001/logs

### 6. Production (5 min)
```bash
# Gateway as daemon
pnpm clawdbot gateway stop  # If foreground
pnpm clawdbot gateway start --daemon
pnpm clawdbot gateway status
```

## 🆘 Rollback

```bash
# Restore Script
~/.skills/clawdbot-update/restore-clawdbot.sh ~/.clawdbot-backups/pre-update-YYYYMMDD-HHMMSS

# Or manually:
cd ~/code/clawdbot
git checkout <old-commit>
pnpm install && pnpm build
cp ~/.clawdbot-backups/pre-update-*/clawdbot.json ~/.clawdbot/
pnpm clawdbot gateway restart
```

## ⚠️ Breaking Changes Check

- [ ] **DM Policy**: Check pairing vs allowlist
- [ ] **Groups**: Verify allowlists (add `"*"` for all)
- [ ] **Sandbox**: Scope explicitly set
- [ ] **Timestamps**: Check if custom parsing needed
- [ ] **Slash Commands**: Authorization works
- [ ] **Model Config**: Doctor migrated

## 📊 Monitoring (24h)

### Logs
```bash
pnpm clawdbot logs --follow
# Or: Web UI → http://localhost:3001/logs
```

### Status
```bash
pnpm clawdbot status
pnpm clawdbot providers list --usage
pnpm clawdbot agents list
```

### Watch For
- [ ] No auth errors in logs
- [ ] Typing indicators work (not stuck)
- [ ] Sandbox containers run
- [ ] Sessions route correctly

## 📝 Configuration Examples

### Multi-Agent Example
```json
{
  "routing": {
    "agents": {
      "main": {
        "name": "Main Assistant",
        "workspace": "~/clawd"
      },
      "work": {
        "name": "Work Assistant",
        "workspace": "~/clawd-work",
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        }
      }
    }
  }
}
```

### Provider DM Policies
```json
{
  "telegram": {
    "dmPolicy": "pairing"
  },
  "whatsapp": {
    "dmPolicy": "allowlist",
    "allowFrom": ["+1234567890", "+9876543210"]
  }
}
```

## 🎯 Success Criteria

✅ Gateway runs stable  
✅ Provider DMs + Groups work  
✅ Multi-Agent routing works (if configured)  
✅ Sandbox isolation works (if configured)  
✅ No auth errors  
✅ No stuck typing indicators  
✅ New CLI tools work  

## 📞 If Problems

1. **Logs**: `pnpm clawdbot logs --grep error`
2. **Doctor**: `pnpm clawdbot doctor`
3. **Restart**: `pnpm clawdbot gateway restart`
4. **Rollback**: Use restore script with backup directory

---

**Backup Location**: `~/.clawdbot-backups/pre-update-*`  
**Update Date**: $(date)  
**Target Version**: v2026.1.8  
**Estimated Time**: 45-60 minutes
