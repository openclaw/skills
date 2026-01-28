---
name: image-optimizer
description: Get AI-powered image optimization suggestions. Use when images are slowing your site.
---

# Image Optimizer

Your images are 5MB each and nobody noticed until Lighthouse screamed. This tool scans your images and tells you exactly what to optimize.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-image-optimize ./public/images/
```

## What It Does

- Scans image directories for optimization opportunities
- Identifies oversized images
- Suggests format conversions (PNG to WebP, etc.)
- Recommends responsive image strategies

## Usage Examples

```bash
# Scan images directory
npx ai-image-optimize ./public/images/

# Scan assets folder
npx ai-image-optimize ./assets/

# Get detailed report
npx ai-image-optimize ./public/ --verbose
```

## Best Practices

- **Use WebP** - smaller than PNG/JPEG with same quality
- **Serve responsive images** - don't send desktop images to mobile
- **Lazy load below the fold** - defer loading offscreen images
- **Compress aggressively** - 80% quality is usually fine

## When to Use This

- Lighthouse says images are too big
- Page load times are slow
- Want to audit image usage
- Planning an optimization sprint

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
npx ai-image-optimize --help
```

## How It Works

Scans your image files, collects metadata like size, dimensions, and format. Sends the analysis to GPT-4o-mini which provides prioritized optimization recommendations.

## License

MIT. Free forever. Use it however you want.
