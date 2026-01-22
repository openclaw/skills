# Krea.ai API Skill

See [SKILL.md](./SKILL.md) for full documentation.

## Quick Start

```bash
# Generate an image (will use clawdbot config if set)
python3 krea_api.py --prompt "A cute crab at a desk" --model flux

# List available models
python3 krea_api.py --list-models
```

## Configure Credentials

```bash
clawdbot config set skill.krea_api.key_id YOUR_KEY_ID
clawdbot config set skill.krea_api.secret YOUR_SECRET
```

## Publish to ClawdHub

```bash
# Login once
clawdhub login

# Publish this skill folder
clawdhub publish /Users/fossilizedcarlos/clawd/skills/krea-api --slug krea-api --name "Krea.ai API" --version 0.1.0 --changelog "Initial release"
```

## Requirements

- Python 3.7+
- No external dependencies (uses stdlib)
