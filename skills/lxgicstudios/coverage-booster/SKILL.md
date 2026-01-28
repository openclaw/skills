---
name: coverage-booster
description: Find untested code paths and generate tests to boost coverage. Use when your test coverage is too low and you need to fill the gaps.
---

# Coverage Booster

Your coverage report says 47%. Your manager says 80%. This tool finds the untested code paths in your project and generates the missing tests. Stop writing boilerplate test code by hand when a tool can find the gaps and fill them for you.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-coverage-boost src/
```

## What It Does

- Scans your source files and identifies functions, branches, and lines without test coverage
- Generates Jest or Vitest compatible test files for the uncovered code
- Prioritizes untested code by complexity so you fix the riskiest stuff first
- Handles edge cases like error handlers and conditional branches
- Outputs ready to run test files that actually pass

## Usage Examples

```bash
# Boost coverage for your whole src directory
npx ai-coverage-boost src/

# Target a specific file
npx ai-coverage-boost src/utils/parser.ts

# Scan all TypeScript files
npx ai-coverage-boost "src/**/*.ts"
```

## Best Practices

- **Run your existing tests first** - Know your baseline before generating new ones
- **Review generated tests** - They're good starting points but might need tweaks for your specific setup
- **Focus on business logic** - Don't waste time boosting coverage on trivial getters and setters
- **Integrate with CI** - Set a coverage threshold and use this tool when you dip below it

## When to Use This

- Coverage dropped below your team's threshold after a big feature push
- You inherited a project with almost no tests
- You need to hit a coverage target for a release gate
- You want to find risky untested code before it bites you in production

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
npx ai-coverage-boost --help
```

## How It Works

The tool scans your source files and compares them against existing test files to find gaps. It identifies untested functions, branches, and error paths, then generates test cases that cover those specific code paths. The output is test files compatible with Jest or Vitest.

## License

MIT. Free forever. Use it however you want.