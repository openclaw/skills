---
name: prefetcher
description: AI suggests routes and data to prefetch for better UX. Use when optimizing navigation performance.
---

# Prefetch Advisor

Your app feels slow between page transitions. This tool analyzes user flows and tells you what to prefetch. Routes, API calls, images. Load them before users even click.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-prefetch ./src
```

## What It Does

- Analyzes your routes and navigation patterns
- Identifies high-probability next pages to prefetch
- Suggests data prefetching for API calls
- Recommends link prefetch and preload strategies
- Works with Next.js, React Router, and vanilla setups

## Usage Examples

```bash
# Analyze all routes
npx ai-prefetch ./src/pages

# Focus on specific user flow
npx ai-prefetch ./src --entry /dashboard

# Include API call analysis
npx ai-prefetch ./src --include-api

# Generate prefetch code
npx ai-prefetch ./src --generate

# Next.js Link prefetch optimization
npx ai-prefetch ./src --framework next
```

## Best Practices

- **Prefetch on hover, not on load** - Wait for intent signals to avoid wasting bandwidth
- **Prioritize likely paths** - Dashboard after login, not settings page
- **Don't prefetch everything** - Pick 2-3 most likely next actions
- **Use idle time** - requestIdleCallback for non-critical prefetches

## When to Use This

- Navigation between pages feels sluggish
- Users commonly follow predictable flows
- You have bandwidth budget to spare
- Optimizing perceived performance, not just metrics

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
npx ai-prefetch --help
```

## How It Works

The tool maps your routing structure and analyzes navigation links. It identifies common user paths based on UI patterns and suggests which resources to preload. AI considers factors like link visibility, user intent signals, and resource sizes.

## License

MIT. Free forever. Use it however you want.
