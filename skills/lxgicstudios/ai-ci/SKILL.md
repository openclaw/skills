---
name: ci-gen
description: Generate GitHub Actions workflows from your project. Use when setting up CI/CD from scratch.
---

# CI Generator

Setting up CI/CD from scratch means searching through docs, copying examples, and tweaking YAML for an hour. This tool looks at your project and generates the right workflow automatically.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-ci
```

## What It Does

- Scans your project to detect language and framework
- Generates complete GitHub Actions workflow
- Configures linting, testing, building, and deployment
- Supports multiple deploy targets

## Usage Examples

```bash
# Generate workflow for current project
npx ai-ci

# Specify deploy target
npx ai-ci --deploy vercel

# Preview without writing
npx ai-ci --preview

# Different targets
npx ai-ci --deploy netlify
npx ai-ci --deploy aws
npx ai-ci --deploy docker
npx ai-ci --deploy fly
```

## Best Practices

- **Start simple** - add complexity as needed
- **Cache dependencies** - speeds up your builds significantly
- **Fail fast** - run quick checks (lint) before slow ones (e2e)
- **Review the output** - understand what it's doing before committing

## When to Use This

- Starting a new project and need CI immediately
- Migrating from another CI system to GitHub Actions
- Want a solid starting point to customize
- Not sure what a modern CI workflow should include

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
npx ai-ci --help
```

## How It Works

Analyzes your package.json, config files, and project structure to determine the language, framework, test setup, and build steps. Then generates a GitHub Actions workflow YAML with appropriate jobs, caching, and deployment configuration.

## License

MIT. Free forever. Use it however you want.
