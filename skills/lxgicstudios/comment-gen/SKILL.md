---
name: comment-gen
description: Add meaningful inline comments to complex code. Use when documentation is lacking.
---

# Comment Generator

Good comments explain WHY, not WHAT. This tool reads your code, understands the intent, and adds comments that actually help future readers.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-comment ./src/algorithm.ts
```

## What It Does

- Adds inline comments explaining the reasoning behind complex code
- Focuses on WHY the code does something, not WHAT it does
- Supports multiple verbosity levels for different audiences
- Preserves your existing formatting

## Usage Examples

```bash
# Add concise comments
npx ai-comment ./src/algorithm.ts

# More detailed explanations
npx ai-comment ./src/utils.js --style detailed

# For junior developer onboarding
npx ai-comment ./src/parser.ts --style beginner

# Preview without changing files
npx ai-comment ./src/complex.ts --dry-run
```

## Best Practices

- **Don't over-comment** - simple code doesn't need comments
- **Focus on complex logic** - business rules, edge cases, workarounds
- **Review the output** - make sure comments are accurate
- **Update when code changes** - stale comments are worse than none

## When to Use This

- Inherited a codebase with no documentation
- Onboarding new team members
- Complex algorithms that need explanation
- Before going on vacation so others can maintain your code

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
npx ai-comment --help
```

## How It Works

Reads your code file, sends it to GPT-4o-mini, and receives the same code with meaningful inline comments added. The AI analyzes control flow, business logic, and edge cases to explain the reasoning.

## License

MIT. Free forever. Use it however you want.
