---
name: apple-mail-search
description: Fast & safe Apple Mail search with body content support.
homepage: https://clawdhub.com/gumadeiras/apple-mail-search-safe
repository: https://github.com/gumadeiras/apple-mail-search-cli
metadata: {"clawdbot":{"emoji":"📧","requires":{"bins":["fruitmail"]},"install":[{"id":"node","kind":"node","package":"apple-mail-search-cli","bins":["fruitmail"],"label":"Install fruitmail CLI (npm)"}]}}
---

# Fruitmail (Fast & Safe)

Fast SQLite-based search for Apple Mail.app with full body content support.

## Installation

```bash
npm install -g apple-mail-search-cli
```

## Usage

```bash
# Complex search
fruitmail search --subject "invoice" --days 30 --unread

# Search by sender
fruitmail sender "@amazon.com"

# List unread emails
fruitmail unread

# Read full email body (supports --json)
fruitmail body 94695

# Open in Mail.app
fruitmail open 94695

# Database stats
fruitmail stats
```

## Commands

| Command | Description |
|---------|-------------|
| `search` | Complex search with filters |
| `sender <query>` | Search by sender email |
| `unread` | List unread emails |
| `body <id>` | Read full email body (AppleScript) |
| `open <id>` | Open email in Mail.app |
| `stats` | Database statistics |

## Search Options

```
--subject <text>   Search subject lines
--days <n>         Last N days
--unread           Only unread emails
--limit <n>        Max results (default: 20)
--json             Output as JSON
--copy             Copy DB before query (safest mode)
```

## Examples

```bash
# Find bank statements from last month
fruitmail search --subject "statement" --days 30

# Get unread emails as JSON
fruitmail unread --json | jq '.[] | .subject'

# Find emails from Amazon
fruitmail sender "@amazon.com" --limit 50
```

## Performance

| Method | Time for 130k emails |
|--------|---------------------|
| AppleScript (full iteration) | 8+ minutes |
| SQLite (this tool) | **~50ms** |

## Technical Details

- **Database:** `~/Library/Mail/V{9,10,11}/MailData/Envelope Index`
- **Query method:** SQLite (read-only) + AppleScript (body content)
- **Safety:** Read-only mode prevents modification; optional `--copy` mode available

## Notes

- **macOS only** — queries Apple Mail.app's local database
- **Read-only** — can search/read but cannot compose/send
- **To send emails:** Use the `himalaya` skill (IMAP/SMTP)

## Source

https://github.com/gumadeiras/apple-mail-search-cli
