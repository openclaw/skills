---
name: onboard-gen
description: Generate onboarding documentation for new developers. Use when setting up new team members.
---

# Onboard Gen

New dev joins your team. They spend two weeks figuring out where things are. This tool generates onboarding docs from your codebase. Architecture overview, setup steps, key concepts. Everything they need to become productive fast.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-onboard ./src
```

## What It Does

- Scans your codebase and generates a getting started guide
- Creates architecture documentation explaining how pieces connect
- Produces setup instructions with environment variables and dependencies
- Documents key concepts, patterns, and conventions in your code
- Generates a FAQ based on common confusion points

## Usage Examples

```bash
# Generate onboarding docs for your project
npx ai-onboard ./src

# Include specific focus areas
npx ai-onboard ./src --focus auth,database,api

# Output as a single markdown file
npx ai-onboard ./src --output ONBOARDING.md
```

## Best Practices

- **Run from project root** - The tool needs context from package.json and config files
- **Keep a README updated** - The tool uses your README as additional context if it exists
- **Review and customize** - Add team-specific info like Slack channels and meeting schedules
- **Regenerate quarterly** - Your codebase changes. So should your onboarding docs.

## When to Use This

- New developer joining your team next week
- Open sourcing a project and need contributor docs
- Your onboarding docs are three years old and mention deprecated services
- Building a team wiki from scratch

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
npx ai-onboard --help
```

## How It Works

The tool analyzes your project structure, reads key files like package.json and config files, samples your source code, then generates documentation that explains how everything fits together. It focuses on what a new developer actually needs to know.

## License

MIT. Free forever. Use it however you want.
