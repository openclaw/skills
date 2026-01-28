---
name: husky-gen
description: Set up git hooks tailored to your project. Use when adding pre-commit hooks.
---

# Husky Generator

Git hooks are powerful but setting them up is a pain. This tool analyzes your project and creates the right hooks for your workflow.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-husky
```

## What It Does

- Installs and configures Husky
- Creates pre-commit hooks for linting staged files
- Sets up pre-push hooks for running tests
- Adds commit-msg hook for conventional commits

## Usage Examples

```bash
# Install git hooks
npx ai-husky

# Preview without installing
npx ai-husky --dry-run
```

## Best Practices

- **Lint staged files only** - don't lint the whole codebase
- **Run tests on push** - catch issues before PR
- **Keep hooks fast** - slow hooks get bypassed
- **Make them skippable** - --no-verify for emergencies

## When to Use This

- Setting up a new project with git hooks
- Adding code quality checks to existing project
- Enforcing commit message format
- Standardizing pre-commit workflow

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
npx ai-husky --help
```

## How It Works

Analyzes your package.json to determine what linters, formatters, and test runners you use. Then generates appropriate Husky hooks that run the right commands at the right times.

## License

MIT. Free forever. Use it however you want.
