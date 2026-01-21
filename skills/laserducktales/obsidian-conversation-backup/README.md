# Obsidian Conversation Backup for Clawdbot

🦞 Automatic conversation backup system with beautiful chat-style Obsidian formatting.

## Features

- ⚡ **Zero token cost** - Pure shell scripting, no LLM calls
- 💾 **Incremental backups** - Hourly snapshots of new messages only
- 💬 **Chat formatting** - Colored Obsidian callouts with emojis and timestamps
- 📊 **Token monitoring** - Telegram warnings at 800k/900k tokens
- 📅 **Hourly breakdowns** - Organize conversations by clock hour
- 🎯 **Smart filtering** - Skips empty messages and system notifications

## Quick Start

```bash
# Install the skill
clawdbot skills install YOUR-USERNAME/clawdbot-obsidian-backup

# Run installer
cd ~/.clawdbot/skills/obsidian-conversation-backup
./install.sh

# Add to crontab for automatic hourly backups
crontab -e
# Add: 0 * * * * /path/to/scripts/monitor_and_save.sh
```

## What It Does

Protects your Clawdbot conversations from data loss when running `/new` by automatically backing up to Obsidian vault with beautiful formatting.

**In Obsidian, conversations look like:**

![Chat format example](https://via.placeholder.com/600x300.png?text=User+%28blue%29+%7C+Assistant+%28green%29+with+timestamps)

🐉 **User** messages in blue callouts  
🦞 **Zoidbot** messages in green callouts

## Documentation

See [SKILL.md](SKILL.md) for complete documentation, configuration options, and advanced usage.

## Requirements

- Clawdbot
- Obsidian vault
- `jq` (JSON parser)
- `cron` (for automatic backups)

## License

MIT License - See LICENSE file

## Contributing

Issues and pull requests welcome!
