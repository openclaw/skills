---
name: cache-strategy
description: Get AI-powered caching strategy suggestions for your API. Use when performance matters.
---

# Cache Strategy

You know you should cache things but you're not sure what, where, or for how long. Point this tool at your API routes and get specific caching recommendations.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-cache-strategy ./src/api/
```

## What It Does

- Analyzes your API endpoints
- Identifies what should be cached
- Recommends TTL values based on data patterns
- Suggests caching layer (CDN, Redis, memory)

## Usage Examples

```bash
# Analyze API routes
npx ai-cache-strategy ./src/api/

# Analyze specific route file
npx ai-cache-strategy ./routes/products.ts

# Get Redis-specific recommendations
npx ai-cache-strategy ./src/api/ --layer redis
```

## Best Practices

- **Cache static data aggressively** - config, reference data, rarely changing content
- **Be careful with user data** - personalized responses need different strategies
- **Invalidate properly** - stale cache is worse than no cache
- **Monitor hit rates** - if nothing is hitting cache, something's wrong

## When to Use This

- API response times are too slow
- Database is getting hammered with repeated queries
- Scaling up and need to reduce load
- Building a new API and want to design caching upfront

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Needs OPENAI_API_KEY environment variable.

```bash
npx ai-cache-strategy --help
```

## How It Works

Reads your API route files, understands the data patterns and access patterns from the code, and recommends appropriate caching strategies. The AI considers factors like data freshness requirements, personalization, and common access patterns.

## License

MIT. Free forever. Use it however you want.
