---
name: wiki-gen
description: Generate a project wiki from your codebase. Use when creating documentation.
---

# Wiki Generator

Your project needs documentation. This scans your codebase and generates a complete wiki.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-wiki ./src/
```

## What It Does

- Scans your codebase
- Generates wiki pages for each module
- Documents architecture and patterns
- Creates navigation structure

## Usage Examples

```bash
# Generate wiki
npx ai-wiki ./src/

# From lib folder
npx ai-wiki ./lib/
```

## Best Practices

- **Keep it updated** - regenerate when code changes
- **Add manual context** - AI misses some nuances
- **Link related pages** - make navigation easy
- **Include examples** - show, don't just tell

## When to Use This

- Creating project documentation
- Onboarding new developers
- Open source projects
- Internal documentation

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Needs OPENAI_API_KEY environment variable.

```bash
npx ai-wiki --help
```

## How It Works

Scans your codebase to understand modules, exports, and relationships. Then generates markdown wiki pages with documentation for each major component.

## License

MIT. Free forever. Use it however you want.
