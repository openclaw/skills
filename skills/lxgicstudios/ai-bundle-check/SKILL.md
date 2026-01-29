---
name: bundle-checker
description: Analyze bundle size and get AI suggestions to reduce it. Use when your builds are getting bloated.
---

# Bundle Checker

Your bundle is 2MB and you don't know why. This tool analyzes your build output and tells you exactly what's eating up space and how to fix it.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-bundle-check
```

## What It Does

- Analyzes your bundle composition
- Identifies the largest dependencies
- Suggests tree-shaking opportunities
- Recommends lighter alternatives

## Usage Examples

```bash
# Analyze current project
npx ai-bundle-check

# Analyze specific directory
npx ai-bundle-check ./my-project/

# Get detailed breakdown
npx ai-bundle-check --verbose
```

## Best Practices

- **Check before shipping** - catch size regressions early
- **Consider alternatives** - moment.js vs date-fns makes a huge difference
- **Dynamic imports** - split code that isn't needed immediately
- **Monitor trends** - track bundle size in CI

## When to Use This

- Your app loads slowly and you suspect the bundle
- Adding a new dependency and want to check the impact
- Performance audit flagged JavaScript size
- CI bundle size check is failing

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
npx ai-bundle-check --help
```

## How It Works

Scans your package.json and build output, identifies heavy dependencies, and sends the analysis to GPT-4o-mini. The AI knows common bundle bloat patterns and suggests specific optimizations like switching libraries or adding tree-shaking config.

## License

MIT. Free forever. Use it however you want.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/ai-bundle-check](https://github.com/lxgicstudios/ai-bundle-check)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
