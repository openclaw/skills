# Testing the HealthKit Sync Skill

This guide explains how to test the `healthkit-sync` Agent Skill in ClawdBot.

## Prerequisites

- ClawdBot CLI installed (`clawdbot --version`)
- ClawdBot gateway configured (`~/.clawdbot/clawdbot.json`)
- Active messaging provider (WhatsApp, Telegram, or Discord)

## Step 1: Link the Skill

ClawdBot loads skills from `~/.clawdbot/skills/`. Create a symlink to keep the skill in sync with the repo:

```bash
# Check if already linked
ls -la ~/.clawdbot/skills/healthkit-sync

# Create symlink (if not exists)
ln -sf "$(pwd)/skills/healthkit-sync" ~/.clawdbot/skills/healthkit-sync

# Verify
ls -la ~/.clawdbot/skills/healthkit-sync/
```

Expected output:
```
SKILL.md
references/
TESTING.md
```

## Step 2: Validate Skill Structure

Verify the skill follows the [Agent Skills specification](https://agentskills.io/specification):

```bash
# Check frontmatter
head -15 ~/.clawdbot/skills/healthkit-sync/SKILL.md
```

Expected frontmatter:
```yaml
---
name: healthkit-sync
description: iOS HealthKit data sync CLI commands and patterns...
license: Apache-2.0
compatibility: macOS with healthsync CLI installed
metadata:
  category: development
  platforms: ios,macos
  author: mneves
---
```

Validation checklist:
- [ ] `name` matches folder name (`healthkit-sync`)
- [ ] `name` is lowercase with hyphens only
- [ ] `description` is under 1024 characters
- [ ] SKILL.md is under 500 lines

```bash
# Check line count
wc -l ~/.clawdbot/skills/healthkit-sync/SKILL.md
# Should be < 500
```

## Step 3: Start a New Session

**Important:** Skills are snapshotted when a session starts. Changes require a new session.

### Option A: Restart Gateway

```bash
# Stop existing gateway (Ctrl+C or kill)
pkill -f "clawdbot gateway"

# Start fresh
clawdbot gateway --port 18789
```

### Option B: New Chat Session

Start a new conversation in your messaging app:
- **WhatsApp**: Send a message from an allowed number
- **Telegram**: Start fresh chat with your bot
- **Discord**: New channel or DM

## Step 4: Test Skill Activation

Send test messages that should trigger the skill. The skill activates when the agent detects relevant keywords in your message.

### Test Cases

| # | Message | Expected Response |
|---|---------|-------------------|
| 1 | "How do I sync health data from my iPhone to my Mac?" | CLI pairing flow (`healthsync discover`, `healthsync scan`) |
| 2 | "What commands does healthsync support?" | Full CLI reference with all commands |
| 3 | "How do I fetch my step count?" | `healthsync fetch` command with `--types steps` |
| 4 | "Explain the security architecture of iOS Health Sync" | mTLS, certificate pinning, Keychain storage details |
| 5 | "What's the project structure of ai-health-sync?" | Architecture overview with file paths |
| 6 | "How does certificate pinning work in healthsync?" | TOFU model, SHA256 fingerprint validation |
| 7 | "Troubleshoot: no devices found" | Troubleshooting steps (WiFi, mDNS, firewall) |

### Verification

A successful skill activation should include:
- Specific CLI commands (not generic advice)
- Correct paths (`~/.healthsync/config.json`)
- Accurate security details (SwiftData for iOS tokens, Keychain for macOS)
- References to project files when relevant

## Step 5: Test Progressive Disclosure

The skill uses progressive disclosure - references load on-demand:

1. **Initial query**: Only SKILL.md content loads (~100-150 lines)
2. **Detailed query**: Reference files load as needed

Test this by asking increasingly specific questions:

```
Message 1: "What is healthsync?"
→ Basic overview from SKILL.md

Message 2: "Show me the detailed CLI reference"
→ Loads references/CLI-REFERENCE.md

Message 3: "Explain the certificate pinning implementation"
→ Loads references/SECURITY.md

Message 4: "What's the full project architecture?"
→ Loads references/ARCHITECTURE.md
```

## Step 6: Debug Issues

### Skill Not Loading

```bash
# Check ClawdBot recognizes the skills directory
cat ~/.clawdbot/clawdbot.json | jq '.skills'

# Verify skill is readable
cat ~/.clawdbot/skills/healthkit-sync/SKILL.md | head -20

# Check for YAML parsing errors (must be valid YAML frontmatter)
```

### Skill Not Activating

The skill activates based on keyword matching in the `description` field. Ensure your message contains relevant terms:
- "healthsync", "health sync"
- "HealthKit", "health data"
- "iPhone", "iOS", "macOS"
- "pairing", "sync", "fetch"
- "certificate pinning", "mTLS"

### Wrong Information Returned

If the agent returns incorrect info, the skill may not be loading. Verify by asking:
```
"What is the config path for healthsync CLI?"
```

Correct answer: `~/.healthsync/config.json`
If wrong: Skill not loaded, check steps 1-3.

## Step 7: Monitor Logs

```bash
# Watch ClawdBot logs in real-time
tail -f ~/.clawdbot/logs/*.log

# Filter for skill-related messages
tail -f ~/.clawdbot/logs/*.log | grep -iE "(skill|healthkit)"
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Skill not found | Symlink broken | Re-run `ln -sf` command |
| Old content returned | Session cached | Start new session |
| YAML parse error | Invalid frontmatter | Check for tabs (use spaces) |
| References not loading | Wrong path syntax | Use `[text](path)` not `[See: file]` |
| Skill ignored | Description mismatch | Add more keywords to description |

## Updating the Skill

After making changes to the skill files:

1. **Git pull** (if changes from repo):
   ```bash
   git pull origin master
   ```

2. **Symlink auto-updates** (if linked correctly)

3. **Start new session** (required for changes to take effect)

## References

- [Agent Skills Specification](https://agentskills.io/specification)
- [ClawdBot Skills Documentation](https://docs.clawd.bot/tools/skills)
- [ClawdBot Skills Config](https://docs.clawd.bot/tools/skills-config)
