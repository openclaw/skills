---
name: audit-fixer
description: Analyze npm audit output with AI and get actionable fix suggestions. Use when dealing with security vulnerabilities.
---

# Audit Fixer

npm audit shows 47 vulnerabilities. Half are in nested dependencies you can't control. This tool analyzes your audit results and gives you actionable fixes. Which ones matter, which to ignore, and exactly what to do about each.

**One command. Zero config. Just works.**

## Quick Start

```bash
npm audit --json | npx ai-audit-fix
```

## What It Does

- Analyzes npm audit output and prioritizes by real risk
- Identifies which vulnerabilities actually affect your code
- Provides specific fix commands for each issue
- Explains when to override vs when to actually fix
- Distinguishes between dev and production dependencies

## Usage Examples

```bash
# Pipe audit output directly
npm audit --json | npx ai-audit-fix

# Analyze from a saved file
npx ai-audit-fix --input audit-results.json

# Only show high and critical issues
npm audit --json | npx ai-audit-fix --severity high,critical

# Get fix commands only
npm audit --json | npx ai-audit-fix --fixes-only
```

## Best Practices

- **Focus on production deps first** - Dev dependencies don't ship to users
- **Check if vulnerable code is actually called** - Many vulnerabilities are in code paths you never use
- **Update parent packages first** - Often fixes multiple nested vulnerabilities at once
- **Use overrides carefully** - Document why you're overriding and set a reminder to revisit

## When to Use This

- npm audit shows a wall of red and you don't know where to start
- CI is failing on security checks
- Need to report on vulnerabilities to a security team
- Deciding whether to delay a release for security fixes

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
npx ai-audit-fix --help
```

## How It Works

The tool parses npm audit JSON output, analyzes each vulnerability's dependency chain and severity, determines if it affects your production code, then generates prioritized recommendations with specific fix commands.

## License

MIT. Free forever. Use it however you want.
