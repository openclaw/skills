---
name: refactor-assist
description: Get refactoring suggestions with colored diffs. Use when improving code quality.
---

# Refactor Assistant

Code review yourself before anyone else does. Point this at a file and get specific refactoring suggestions with diffs.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-refactor src/utils.ts
```

## What It Does

- Analyzes code for improvement opportunities
- Shows colored diffs for suggested changes
- Focuses on readability and patterns
- Can apply changes automatically

## Usage Examples

```bash
# See suggestions
npx ai-refactor src/utils.ts

# Apply changes directly
npx ai-refactor src/utils.ts --apply

# Focus on specific area
npx ai-refactor src/api.ts --focus "error handling"
```

## Best Practices

- **Review before applying** - verify suggestions make sense
- **Commit first** - have a clean state to diff against
- **Focus on one thing** - don't refactor everything at once
- **Run tests after** - make sure nothing broke

## When to Use This

- Code review prep
- Cleaning up old code
- Learning better patterns
- Technical debt sprints

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
npx ai-refactor --help
```

## How It Works

Reads your file, sends it to GPT-4o-mini for analysis, and shows refactoring suggestions as diffs. Looks at readability, duplication, modern patterns, performance, and type safety.

## License

MIT. Free forever. Use it however you want.
