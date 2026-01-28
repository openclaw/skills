# ai-husky

Set up git hooks tailored to your project. Analyzes your package.json and creates pre-commit, pre-push, and commit-msg hooks.

## Install

```bash
npm install -g ai-husky
```

## Usage

```bash
npx ai-husky
# → Git hooks installed in .husky/

npx ai-husky --dry-run
# → Preview the hooks without installing
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## What it creates

- **pre-commit** - Lints staged files, runs type-check
- **pre-push** - Runs your test suite
- **commit-msg** - Validates conventional commit format

## License

MIT
