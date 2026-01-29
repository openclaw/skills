---
name: cloudflare-gen
description: Generate Cloudflare Workers configuration and code. Use when building on the edge.
---

# Cloudflare Gen

Cloudflare Workers are powerful but wrangler.toml syntax is its own thing. This tool generates Worker code and configuration from plain English. Edge functions, KV storage, R2 buckets. All set up correctly.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-cloudflare "API proxy with rate limiting"
```

## What It Does

- Generates wrangler.toml configuration
- Creates Worker TypeScript/JavaScript code
- Sets up KV namespaces and R2 bindings
- Includes proper routing and middleware
- Handles environment variables and secrets

## Usage Examples

```bash
# Simple Worker
npx ai-cloudflare "redirect based on country"

# API with storage
npx ai-cloudflare "REST API with KV storage for user preferences"

# Edge caching
npx ai-cloudflare "cache API responses at the edge for 1 hour"

# Auth middleware
npx ai-cloudflare "JWT validation middleware for API routes"
```

## Best Practices

- **Keep Workers small** - Edge has size limits
- **Use KV for reads** - KV is fast for reads, slow for writes
- **Handle errors** - Edge errors are hard to debug, be explicit
- **Test locally** - wrangler dev before deploying

## When to Use This

- Building serverless functions on Cloudflare
- Need edge computing for latency-sensitive features
- Setting up Cloudflare Pages with Workers
- Learning Workers and want working examples

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgicstudios.com

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Requires OPENAI_API_KEY environment variable.

```bash
export OPENAI_API_KEY=sk-...
npx ai-cloudflare --help
```

## How It Works

Takes your description and generates both the Worker code and wrangler.toml configuration. Sets up proper bindings for KV, R2, or Durable Objects if needed. The code follows Cloudflare's patterns and handles common edge cases.

## License

MIT. Free forever. Use it however you want.
