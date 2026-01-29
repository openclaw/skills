---
name: deps-analyzer
description: Find unused and outdated dependencies. Use when your package.json is a mess.
---

# Deps Analyzer

Your package.json has 87 dependencies and you use maybe 40 of them. This tool finds the dead weight and tells you what to do about it.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-deps
```

## What It Does

- Finds unused dependencies you can remove
- Flags outdated packages with security issues
- Explains what each problematic dependency does
- Can auto-fix by removing unused deps

## Usage Examples

```bash
# Audit current project
npx ai-deps

# Auto-remove unused deps
npx ai-deps --fix

# Check a specific directory
npx ai-deps --dir ./my-project
```

## Best Practices

- **Run before major updates** - clean slate before upgrading
- **Check devDependencies too** - test tools get stale
- **Review before fixing** - some deps are used dynamically
- **Update lockfile after** - run npm install after removals

## When to Use This

- Your install is taking forever
- Bundle size is way too big
- npm audit has 47 warnings
- You inherited a project with mystery deps

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
npx ai-deps --help
```

## How It Works

Runs depcheck to find unused dependencies and npm outdated to find stale ones. Sends the results to GPT-4o-mini for analysis, which explains each issue and prioritizes what to fix first.

## License

MIT. Free forever. Use it however you want.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/ai-deps](https://github.com/lxgicstudios/ai-deps)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
