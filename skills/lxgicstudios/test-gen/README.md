# ai-test-gen

[![npm version](https://img.shields.io/npm/v/ai-test-gen.svg)](https://www.npmjs.com/package/ai-test-gen)
[![npm downloads](https://img.shields.io/npm/dm/ai-test-gen.svg)](https://www.npmjs.com/package/ai-test-gen)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered unit test generation from source files. Supports Jest, Vitest, and Mocha.

Point it at your source files and it writes unit tests for you. Supports Jest, Vitest, and Mocha.

## Install

```bash
npm install -g ai-test-gen
```

## Setup

```bash
export OPENAI_API_KEY=sk-your-key-here
```

## Usage

```bash
# Generate Jest tests for a file
npx ai-test-gen src/utils.ts --framework jest

# Vitest instead
npx ai-test-gen src/utils.ts --framework vitest

# Multiple files
npx ai-test-gen "src/**/*.ts" --framework jest

# Save to a file
npx ai-test-gen src/utils.ts --framework jest -o src/__tests__/utils.test.ts
```

## What you get

Actual test files with imports, describe blocks, and test cases. It covers happy paths, edge cases, and error handling. You'll probably want to tweak them a bit, but it beats starting from scratch.

## Heads up

The generated tests are a starting point. They won't know about your mocks, test utilities, or specific setup. But they'll get you 80% there, which is the annoying part anyway.
