# ai-refactor

[![npm version](https://img.shields.io/npm/v/ai-refactor.svg)](https://www.npmjs.com/package/ai-refactor)
[![npm downloads](https://img.shields.io/npm/dm/ai-refactor.svg)](https://www.npmjs.com/package/ai-refactor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered code refactoring with colored diffs. Like having a code review buddy who doesn't get tired.

Point it at a file and get refactoring suggestions with colored diffs. Like having a code review buddy who doesn't get tired.

## Install

```bash
npm install -g ai-refactor
```

## Usage

```bash
# See suggestions
npx ai-refactor src/utils.ts

# Apply changes directly
npx ai-refactor src/utils.ts --apply

# Focus on something specific
npx ai-refactor src/api.ts --focus "error handling"
```

## Setup

```bash
export OPENAI_API_KEY=your-key-here
```

## Options

- `--apply` - Write the refactored code back to the file
- `--focus <area>` - Zero in on a specific concern

## What it looks at

- Readability and naming
- Duplication
- Modern language patterns
- Performance gotchas
- Type safety

It won't change what your code does. Just how it's written.

## License

MIT
