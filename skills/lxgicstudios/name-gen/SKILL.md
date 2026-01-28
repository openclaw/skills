---
name: name-gen
description: Suggest better variable and function names in your code. Use when your code needs clearer naming.
---

# Name Gen

Bad variable names make code unreadable. We've all written "temp", "data", "result", or "x" when we couldn't think of something better. This tool reads your code file and suggests clearer, more descriptive names for variables, functions, and classes. It's like a naming code review.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-naming src/utils.ts
```

## What It Does

- Analyzes code files for poorly named variables and functions
- Suggests clearer, more descriptive alternatives
- Understands context to provide meaningful recommendations
- Works with any programming language
- Prints suggestions right to your terminal

## Usage Examples

```bash
# Analyze a TypeScript file
npx ai-naming src/utils.ts

# Check a Python script
npx ai-naming scripts/process_data.py

# Review a component file
npx ai-naming src/components/Card.tsx
```

## Best Practices

- **Run it on old code first** - Your oldest code probably has the worst names. Start there for the biggest impact
- **Focus on public APIs** - Public function and class names matter most since other developers read them
- **Use it during refactoring** - When you're already changing code, it's the perfect time to improve names too

## When to Use This

- Cleaning up code before a big refactor
- Improving readability of code you inherited
- Getting a second opinion on your naming choices
- Preparing code for open source where clarity matters

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended.

```bash
npx ai-naming --help
```

## How It Works

The tool reads your source file and sends it to an AI model that understands programming conventions and naming patterns. It identifies variables, functions, and classes with unclear names and suggests specific alternatives with explanations.

## License

MIT. Free forever. Use it however you want.