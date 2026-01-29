---
name: stash-namer
description: Generate meaningful git stash names from your changes. Use when stashing work.
---

# Stash Namer

Stop naming stashes "WIP" or leaving them unnamed. This reads your changes and creates a meaningful stash name.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-stash-name
```

## What It Does

- Reads your staged and unstaged changes
- Generates a descriptive stash name
- Actually runs git stash with the name
- No more mystery stashes

## Usage Examples

```bash
# Stash with auto-generated name
npx ai-stash-name

# Preview without stashing
npx ai-stash-name --dry-run
```

## Best Practices

- **Stash early, stash often** - it's free
- **Name them well** - future you will thank you
- **Don't hoard stashes** - apply or drop them
- **Pop, don't apply** - unless you need to keep it

## When to Use This

- Switching contexts quickly
- Saving work before pulling
- Experimenting with changes
- Any time you'd use git stash

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgicstudios.com

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Needs OPENAI_API_KEY environment variable.

```bash
npx ai-stash-name --help
```

## How It Works

Runs git diff to see your changes, sends the diff summary to GPT-4o-mini to generate a descriptive name, then runs git stash push -m with that name.

## License

MIT. Free forever. Use it however you want.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/stash-name-gen](https://github.com/lxgicstudios/stash-name-gen)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
