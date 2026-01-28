# ai-audit-fix

Analyze npm audit output with AI and get clear, actionable fix suggestions instead of cryptic vulnerability reports.

## Install

```bash
npm install -g ai-audit-fix
```

## Usage

```bash
npx ai-audit-fix
```

Run it in any project with a `package.json`. It runs `npm audit` under the hood, sends the results to GPT-4o-mini, and gives you a plain English breakdown with exact fix commands.

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## What you get

- Vulnerability summary (critical/high/moderate/low counts)
- Plain English explanation of each issue
- Exact commands to fix them

## License

MIT
