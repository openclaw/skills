---
name: core-vitals-fixer
description: Fix Core Web Vitals issues with AI guidance. Use when your Lighthouse scores are bad.
---

# Core Web Vitals Fixer

Your LCP is 4 seconds, CLS keeps jumping, and FID feels sluggish. This tool scans your code and tells you exactly what to fix and how.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-core-vitals ./src/
```

## What It Does

- Analyzes your code for Core Web Vitals issues
- Identifies LCP, FID, and CLS problems
- Provides specific fixes with code examples
- Prioritizes issues by impact

## Usage Examples

```bash
# Scan your source directory
npx ai-core-vitals ./src/

# Scan app directory
npx ai-core-vitals ./app/

# Focus on specific metric
npx ai-core-vitals ./src/ --metric lcp
```

## Best Practices

- **Fix LCP first** - it's usually the biggest win
- **Lazy load below the fold** - don't load what users can't see
- **Reserve space for images** - prevents CLS
- **Defer non-critical JS** - improves FID

## When to Use This

- Lighthouse scores are tanking your SEO
- Users complain about slow page loads
- Core Web Vitals failing in Search Console
- Building a new site and want to start optimized

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
npx ai-core-vitals --help
```

## How It Works

Scans your code files for common performance antipatterns, then sends them to GPT-4o-mini. The AI identifies issues affecting LCP, CLS, and FID and provides actionable fixes with priority rankings.

## License

MIT. Free forever. Use it however you want.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/ai-core-vitals](https://github.com/lxgicstudios/ai-core-vitals)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
