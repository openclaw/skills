---
name: test-writer
description: Generate unit tests from source files. Use when you need test coverage fast.
---

# Test Writer

You know that feeling when you finish building something and realize you haven't written a single test? Yeah. This tool takes your source files and generates real unit tests. Pick your framework, point it at your code, and get tests that actually cover your functions. Not placeholder garbage, real assertions based on what your code does.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-test-gen src/utils.ts
```

## What It Does

- Reads your source files and understands the function signatures and logic
- Generates unit tests with real assertions, not just empty describe blocks
- Supports Jest, Vitest, and Mocha out of the box
- Accepts glob patterns so you can test multiple files at once
- Writes output to a file or prints to stdout

## Usage Examples

```bash
# Generate Jest tests for a single file
npx ai-test-gen src/utils.ts

# Generate Vitest tests and save to a file
npx ai-test-gen src/helpers.ts --framework vitest -o tests/helpers.test.ts

# Test multiple files with a glob
npx ai-test-gen "src/**/*.ts" --framework mocha
```

## Best Practices

- **Start with utility functions** - Pure functions with clear inputs and outputs get the best generated tests. Start there, then move to more complex code.
- **Pick the right framework** - Use --framework to match what your project already uses. Mixing test frameworks is a headache nobody needs.
- **Review edge cases** - The generated tests cover the happy path well. Add your own edge cases for null inputs, empty arrays, and boundary conditions.
- **Use it as a starting point** - Generated tests are a great foundation. Tweak them to match your team's testing style.

## When to Use This

- You're adding tests to a project that has none
- You just wrote a bunch of utility functions and need coverage
- You want a starting point for tests instead of writing boilerplate from scratch
- Code review requires tests and you're short on time

## How It Works

The tool reads your source files and analyzes function signatures, types, and logic flow. It sends that context to an AI model that generates test cases with meaningful assertions. You pick the framework and it formats everything to match.

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended.

```bash
npx ai-test-gen --help
```

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## License

MIT. Free forever. Use it however you want.