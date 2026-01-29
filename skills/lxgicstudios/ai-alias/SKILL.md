---
name: alias-gen
description: Generate shell aliases from your command history. Use when streamlining your terminal workflow.
---

# Shell Alias Generator

Analyzes your command history and suggests aliases for commands you type all the time. Stop typing git checkout when you could type gco.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-alias
```

## What It Does

- Reads your shell history (bash, zsh, fish)
- Finds frequently typed long commands
- Generates memorable aliases
- Creates proper shell syntax for your environment
- Groups related commands together

## Usage Examples

```bash
# Analyze and suggest aliases
npx ai-alias

# Generate for specific shell
npx ai-alias --shell zsh

# From specific commands
npx ai-alias "docker compose up, git status, npm run dev"
```

## Best Practices

- **Keep them short** - 2-4 characters ideal
- **Make them memorable** - gc for git commit, not x7
- **Avoid conflicts** - Don't override existing commands
- **Document them** - Comment your aliases file

## When to Use This

- You notice yourself typing the same commands daily
- Setting up a new machine
- Teaching someone your workflow
- Auditing which commands you use most

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgicstudios.com

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended.

```bash
npx ai-alias --help
```

## How It Works

The tool parses your shell history file, counts command frequency, filters out commands with sensitive data, and generates alias definitions. It uses naming conventions that make aliases easy to remember.

## License

MIT. Free forever. Use it however you want.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/ai-alias](https://github.com/lxgicstudios/ai-alias)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
