---
name: branch-namer
description: Generate descriptive git branch names from plain English. Use when you need a branch name that follows conventions.
---

# Branch Namer

Naming branches is harder than it should be. Is it feature/user-auth or feat/add-user-authentication? This tool generates consistent, conventional branch names from plain English descriptions.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-branch "add user authentication with OAuth"
```

## What It Does

- Generates branch names following common conventions (feature/, bugfix/, hotfix/)
- Keeps names short but descriptive
- Uses kebab-case consistently
- Can create the branch for you with --create flag
- Supports custom prefixes and formats

## Usage Examples

```bash
# Get a branch name suggestion
npx ai-branch "fix the login button not working on mobile"

# Create the branch immediately
npx ai-branch "add dark mode support" --create

# Use a specific prefix
npx ai-branch "update dependencies" --prefix chore

# Include ticket number
npx ai-branch "user profile page crashes on load" --ticket PROJ-123
```

## Best Practices

- **Be specific in your description** - "fix bug" gives worse results than "fix crash when user has no profile photo"
- **Include context** - Mention the feature area: "checkout flow: add shipping address validation"
- **Use --create sparingly** - Review the suggestion first, especially on shared repos
- **Match team conventions** - If your team uses different prefixes, use --prefix

## When to Use This

- Starting a new feature and blanking on a good branch name
- Want consistent naming across your team
- Working on multiple tasks and need to track what each branch does
- Onboarding and not sure what naming conventions the team uses

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Requires OPENAI_API_KEY environment variable.

```bash
export OPENAI_API_KEY=sk-...
npx ai-branch --help
```

## How It Works

Takes your description and determines the appropriate branch type (feature, fix, chore, etc.). Extracts key terms and creates a concise, readable branch name following conventional naming patterns. Can optionally run git checkout -b for you.

## License

MIT. Free forever. Use it however you want.
