---
name: lighthouse-fixer
description: Run Lighthouse audit and get AI fix suggestions. Use when improving performance.
---

# Lighthouse Fixer

Lighthouse tells you what's wrong but the fix suggestions are generic. This tool runs Lighthouse and gives you specific, actionable fixes for your issues.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-lighthouse https://mysite.com
```

## What It Does

- Runs full Lighthouse audit on any URL
- Analyzes the results with AI
- Provides specific fixes, not generic advice
- Prioritizes issues by impact

## Usage Examples

```bash
# Audit your site
npx ai-lighthouse https://mysite.com

# Specific page
npx ai-lighthouse https://example.com/page

# Focus on performance
npx ai-lighthouse https://mysite.com --category performance
```

## Best Practices

- **Fix performance first** - biggest impact on user experience
- **Test on slow connections** - not everyone has gigabit
- **Check mobile separately** - mobile scores are often worse
- **Iterate** - fix one thing at a time

## When to Use This

- Lighthouse scores are tanking
- SEO audit flagged performance issues
- Core Web Vitals are failing
- Want actionable advice, not documentation links

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgicstudios.com

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Needs OPENAI_API_KEY environment variable.

```bash
npx ai-lighthouse --help
```

## How It Works

Runs Lighthouse against your URL, captures the full report, and sends it to GPT-4o-mini. The AI interprets the findings and provides specific code-level recommendations based on the actual issues found.

## License

MIT. Free forever. Use it however you want.
