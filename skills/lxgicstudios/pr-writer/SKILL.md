---
name: pr-writer
description: Generate PR titles and descriptions from your branch diff. Use when you need to write pull request descriptions quickly.
---

# PR Writer

Writing PR descriptions is one of those things nobody wants to do but everybody benefits from. You finish a feature branch, you know exactly what changed, but translating that into a clear PR title and description feels like busywork. This tool reads your git diff and writes the whole thing for you.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-pr-desc
```

## What It Does

- Reads the diff between your current branch and the base branch (defaults to main)
- Generates a clear, descriptive PR title that actually summarizes the change
- Writes a full PR description covering what changed and why
- Supports custom base branches with the --base flag
- Works in any git repo without any setup

## Usage Examples

```bash
# Generate PR description against main branch
npx ai-pr-desc

# Generate against a different base branch
npx ai-pr-desc --base develop

# Generate against a release branch
npx ai-pr-desc --base release/v2.0
```

## Best Practices

- **Commit before running** - The tool diffs committed changes, so make sure your work is committed first
- **Keep branches focused** - Smaller, focused branches produce better descriptions than massive multi-feature branches
- **Review the output** - AI gets you 90% there. Spend 30 seconds tweaking the result for your team's style
- **Use with CI** - Pipe the output into your GitHub CLI or API calls to automate PR creation entirely

## When to Use This

- You just finished a feature and need to open a PR fast
- You are working on multiple PRs and don't want to write descriptions for each one
- Your team requires detailed PR descriptions but you'd rather ship code
- You want consistent, well-structured PR descriptions across your team

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
npx ai-pr-desc --help
```

## How It Works

The tool uses simple-git to grab the diff between your current branch and the base branch. It sends that diff to OpenAI, which analyzes the changes and generates a title and description that actually reflects what you built. The output prints straight to your terminal so you can copy it into your PR.

## License

MIT. Free forever. Use it however you want.