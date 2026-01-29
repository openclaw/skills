---
name: changelog-gen
description: Generate changelogs from git history. Use when you need release notes fast.
---

# Changelog Generator

Writing changelogs by hand is tedious. This tool reads your git history between two refs and generates a properly categorized changelog entry. No more copy-pasting commit messages.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-changelog --from v1.0.0 --to v2.0.0
```

## What It Does

- Reads git log between any two refs (tags, branches, commits)
- Groups commits into Added, Changed, Fixed, Removed
- Cleans up messy commit messages into readable entries
- Outputs markdown ready for your CHANGELOG.md

## Usage Examples

```bash
# Between two tags
npx ai-changelog --from v1.0.0 --to v2.0.0

# From a tag to HEAD
npx ai-changelog --from v1.0.0 --to HEAD

# Write directly to file
npx ai-changelog --from v1.0.0 --to v2.0.0 -o CHANGELOG.md

# Specific commit range
npx ai-changelog --from abc123 --to def456
```

## Best Practices

- **Tag your releases** - makes generating changelogs way easier
- **Write decent commits** - garbage in, garbage out
- **Review the output** - AI might miscategorize some changes
- **Run before release** - make it part of your release checklist

## When to Use This

- Preparing a release and need changelog entries
- You forgot to maintain the changelog and need to catch up
- Want consistent changelog formatting across releases
- Generating release notes for GitHub releases

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
npx ai-changelog --help
```

## How It Works

Runs git log between your specified refs, collects all commit messages, and sends them to GPT-4o-mini. The AI parses the commits, understands what each change does, and formats them into proper Keep a Changelog style with appropriate categories.

## License

MIT. Free forever. Use it however you want.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/ai-changelog](https://github.com/lxgicstudios/ai-changelog)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
