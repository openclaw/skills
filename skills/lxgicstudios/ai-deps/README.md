# ai-deps

Your package.json is probably a mess. This tool finds unused dependencies, flags outdated ones, and tells you what to do about it.

## Install

```bash
npm install -g ai-deps
```

## Usage

```bash
# Audit current project
npx ai-deps

# Auto-fix (removes unused deps)
npx ai-deps --fix

# Check a specific directory
npx ai-deps --dir ./my-project
```

## What it does

1. Runs depcheck to find unused dependencies
2. Checks for outdated packages
3. Asks OpenAI to analyze the results and give you actionable advice
4. Optionally removes unused deps for you

## Requirements

Set your `OPENAI_API_KEY` environment variable.

```bash
export OPENAI_API_KEY=sk-...
```

## License

MIT
