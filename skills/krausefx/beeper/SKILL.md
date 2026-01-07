---
name: beeper
description: Search and browse local Beeper chat history (threads, messages, full-text search).
homepage: https://github.com/krausefx/beeper-cli
metadata: {"clawdbot":{"emoji":"🛰️","os":["darwin","linux"],"requires":{"bins":["beeper-cli"]},"install":[{"id":"go","kind":"go","pkg":"github.com/krausefx/beeper-cli/cmd/beeper-cli","bins":["beeper-cli"],"label":"Install beeper-cli (go install)"}]}}
---

# Beeper CLI

[Beeper](https://www.beeper.com/) is a universal chat app that unifies messages from WhatsApp, Telegram, Signal, iMessage, Discord, and more in a single inbox.

This skill provides **read-only access** to your local Beeper chat history. Browse threads, search messages, and extract conversation data.

## Requirements
- Beeper Desktop app installed (provides the SQLite database)
- `beeper-cli` binary on PATH

## Database Path
The CLI auto-detects:
- `~/Library/Application Support/BeeperTexts/index.db` (macOS)
- `~/Library/Application Support/Beeper/index.db` (macOS)

Override with:
- `--db /path/to/index.db`
- `BEEPER_DB=/path/to/index.db`

## Commands

### List Threads
```bash
beeper-cli threads list --days 7 --limit 50 --json
```

### Show Thread Details
```bash
beeper-cli threads show --id "!abc123:beeper.local" --json
```

### List Messages in Thread
```bash
beeper-cli messages list --thread "!abc123:beeper.local" --limit 50 --json
```

### Search Messages (Full-Text)
```bash
# Simple search
beeper-cli search 'invoice' --limit 20 --json

# Phrase search
beeper-cli search '"christmas party"' --limit 20 --json

# Proximity search
beeper-cli search 'party NEAR/5 christmas' --limit 20 --json

# With context window (messages before/after match)
beeper-cli search 'meeting' --context 6 --window 60m --json
```

### Database Info
```bash
beeper-cli db info --json
```

## Notes
- **Read-only**: This tool never sends messages
- **JSON output**: Always use `--json` for structured output agents can parse
- **FTS5 search**: Uses Beeper's built-in full-text index (FTS5) for fast search
- **DM name resolution**: Optionally resolves DM names via bridge databases (disable with `--no-bridge`)

## Installation

### Option 1: Go Install (recommended)
```bash
go install github.com/krausefx/beeper-cli/cmd/beeper-cli@latest
```

### Option 2: Build from Source
```bash
git clone https://github.com/krausefx/beeper-cli.git
cd beeper-cli
go build ./cmd/beeper-cli
# Move beeper-cli to PATH, e.g., /usr/local/bin
```

## Examples

Search for work-related messages from last week:
```bash
beeper-cli threads list --days 7 --json | jq '.threads[] | select(.name | contains("work"))'
beeper-cli search 'project deadline' --limit 10 --json
```

Find messages about invoices with context:
```bash
beeper-cli search 'invoice' --context 3 --json
```
