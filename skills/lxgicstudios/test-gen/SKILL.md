---
name: test-gen
description: Generate unit tests from source files using AI. Use when adding test coverage.
---

# Test Gen

Your code has 12% test coverage and your manager is asking questions. This tool generates unit tests from your source files. Covers happy paths, edge cases, error conditions. Tests that actually test something, not just exist for coverage numbers.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-test-gen ./src/utils.ts
```

## What It Does

- Generates unit tests for your functions and classes
- Covers happy path, edge cases, and error conditions
- Creates tests for Jest, Vitest, or Mocha
- Mocks dependencies automatically
- Includes meaningful assertions, not just "expect(true).toBe(true)"

## Usage Examples

```bash
# Generate tests for a single file
npx ai-test-gen ./src/auth.ts

# Generate for all files in a directory
npx ai-test-gen ./src/services/

# Specify test framework
npx ai-test-gen ./src/utils.ts --framework vitest

# Output to a specific location
npx ai-test-gen ./src/parser.ts --output ./tests/parser.test.ts
```

## Best Practices

- **Review generated tests** - AI tests are a starting point, not a finish line
- **Run them immediately** - Catch issues while context is fresh
- **Add your own edge cases** - You know your domain better than AI
- **Don't trust coverage alone** - Good tests test behavior, not lines

## When to Use This

- Inheriting a codebase with no tests
- Adding tests to a new feature quickly
- Hitting a coverage target for CI
- Learning what good tests look like for your code

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgicstudios.com

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended.

```bash
npx ai-test-gen --help
```

## How It Works

The tool parses your source file, identifies testable units (functions, classes, methods), analyzes their signatures and implementations, then generates test cases that cover normal operation, edge cases, and error handling.

## License

MIT. Free forever. Use it however you want.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/test-gen](https://github.com/lxgicstudios/test-gen)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
