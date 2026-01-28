---
name: codemod-gen
description: Generate codemods for large-scale code changes. Use when refactoring patterns across many files.
---

# Codemod Generator

You need to replace a pattern across 500 files. Find and replace won't cut it. This tool generates AST-based codemods that safely transform your code at scale.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-codemod "convert class components to functional"
```

## What It Does

- Generates jscodeshift codemods for your specific transformation
- Handles complex patterns like class to function conversions
- Preserves formatting and comments
- Works across entire codebases

## Usage Examples

```bash
# Class to functional components
npx ai-codemod "convert class components to functional"

# Modernize code
npx ai-codemod "replace lodash.get with optional chaining"

# API migrations
npx ai-codemod "migrate from moment to date-fns"

# Framework upgrades
npx ai-codemod "update React Router v5 to v6"
```

## Best Practices

- **Test on a branch first** - always run codemods on a fresh branch
- **Review the diff** - spot check that transformations are correct
- **Run incrementally** - do one file type at a time
- **Keep the codemod** - save it for future use

## When to Use This

- Major framework or library upgrades
- Enforcing new code patterns across the codebase
- Deprecating old APIs in favor of new ones
- Standardizing code style at scale

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
npx ai-codemod --help
```

## How It Works

Takes your plain English description of the transformation and generates a jscodeshift codemod script. The AI understands AST manipulation and outputs a codemod you can run with jscodeshift or babel.

## License

MIT. Free forever. Use it however you want.
