---
name: jsdoc-gen
description: Add JSDoc or TSDoc comments to your code. Use when documentation is missing.
---

# JSDoc Generator

Your exported functions have no documentation. This tool adds JSDoc or TSDoc comments to all your exports without touching the actual code logic.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-docs src/ --style jsdoc
```

## What It Does

- Adds JSDoc/TSDoc comments to exported functions and classes
- Describes parameters, return values, and exceptions
- Preserves all existing code and comments
- Works on files, directories, or glob patterns

## Usage Examples

```bash
# Preview docs for a directory
npx ai-docs src/ --style jsdoc

# TSDoc style
npx ai-docs src/ --style tsdoc

# Write changes to files
npx ai-docs src/ --style jsdoc --write

# Single file
npx ai-docs src/utils.ts --style jsdoc

# Glob patterns
npx ai-docs "src/**/*.ts" --style tsdoc
```

## Best Practices

- **Preview first** - run without --write to see what changes
- **Focus on exports** - internal helpers don't need docs
- **Add examples** - especially for complex functions
- **Review output** - AI might miss nuances

## When to Use This

- Codebase has zero documentation
- Onboarding requires reading every function
- IDE hints are unhelpful without docs
- Preparing for open source release

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
npx ai-docs --help
```

## How It Works

Reads your files, identifies exported functions, classes, and types, then generates appropriate documentation comments. The AI understands the function signatures and infers what each parameter does.

## License

MIT. Free forever. Use it however you want.
