# Dex CRM Skill for Clawdbot

Manage your [Dex](https://getdex.com) personal CRM directly from Clawdbot. Search contacts, add notes, manage reminders.

## Installation

### Via ClawdHub (recommended)

```bash
clawdhub install dex-crm
```

### Manual Installation

Copy the `SKILL.md` file to your Clawdbot skills directory:

```bash
cp SKILL.md ~/.clawdbot/skills/dex-crm/SKILL.md
# or for workspace installs:
cp SKILL.md ~/clawd/skills/dex-crm/SKILL.md
```

## Setup

1. Get your Dex API key from [Dex Settings](https://getdex.com/settings/api)

2. Add it to your Clawdbot gateway config (`config.yaml`):

```yaml
env:
  DEX_API_KEY: "your-api-key-here"
```

3. Restart the gateway:

```bash
clawdbot gateway restart
```

## Features

- **Search contacts** by email or browse all contacts
- **View contact details** — phone, email, birthday, notes
- **Add notes** to contacts with timestamps
- **Create/complete reminders** for follow-ups
- **Create new contacts** from conversations
- **Archive contacts** you no longer need

## Example Usage

> "Find John Smith in my Dex contacts"

> "Add a note to Sarah's contact: Met for coffee, discussed the project proposal"

> "Create a reminder to follow up with Mike next Tuesday"

> "Show me all my reminders due this week"

## Included Scripts

### `scripts/dex-cleanup.py`

Automatically archives junk/newsletter contacts from Dex. Useful for cleaning up contacts imported from email that aren't real people.

```bash
# Set your API key
export DEX_API_KEY="your-key"

# Dry run (preview what would be archived)
python3 scripts/dex-cleanup.py --dry-run

# Actually archive junk contacts
python3 scripts/dex-cleanup.py
```

The script identifies junk contacts by patterns like:
- Substack newsletters
- Noreply addresses
- Calendar system entries
- Common newsletter domains

## API Reference

See `SKILL.md` for the complete API reference including all endpoints for contacts, notes, and reminders.

## License

MIT

## Author

Jay Graves ([@jaybna](https://github.com/jaybna))
