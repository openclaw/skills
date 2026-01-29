---
name: script-gen
description: Generate package.json scripts with AI. Use when setting up npm scripts.
---

# Script Generator

Package.json scripts are powerful but writing them is tedious. Describe what you need and get proper npm scripts.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-script "lint, test, build, deploy"
```

## What It Does

- Generates npm scripts for your workflow
- Handles complex script chains
- Includes pre/post hooks
- Works with any tooling

## Usage Examples

```bash
# Basic workflow
npx ai-script "lint, test, build, deploy"

# Docker workflow
npx ai-script "docker build, docker push, k8s deploy"

# Full CI
npx ai-script "typecheck, lint, test:unit, test:e2e, build, deploy:staging"
```

## Best Practices

- **Use pre/post hooks** - run lint before test
- **Keep them composable** - small scripts that chain
- **Document complex ones** - add comments
- **Test locally** - before CI runs them

## When to Use This

- Setting up new project scripts
- Adding CI/CD commands
- Standardizing workflow
- Learning npm script patterns

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
npx ai-script --help
```

## How It Works

Takes your workflow description and generates proper npm scripts with correct syntax. Understands common patterns and generates scripts that work together.

## License

MIT. Free forever. Use it however you want.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/npm-script-gen](https://github.com/lxgicstudios/npm-script-gen)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
