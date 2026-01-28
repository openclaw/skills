---
name: tailwind-config-gen
description: Generate tailwind.config.js from brand colors. Use when setting up Tailwind.
---

# Tailwind Config Generator

You have brand colors and need a complete Tailwind config. This generates a full theme from your palette.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-tailwind "#FF4500" "#1A1A2E"
```

## What It Does

- Takes your brand colors
- Generates complete color palette
- Creates tailwind.config.js
- Includes shades and semantic colors

## Usage Examples

```bash
# Two colors
npx ai-tailwind "#FF4500" "#1A1A2E"

# Three colors
npx ai-tailwind "#3B82F6" "#10B981" "#F59E0B" -o tailwind.config.js
```

## Best Practices

- **Start with brand colors** - primary and accent
- **Generate shades** - 50 through 950
- **Include semantic colors** - success, error, warning
- **Test contrast** - accessibility matters

## When to Use This

- Setting up new Tailwind project
- Implementing brand guidelines
- Creating design system
- Generating color palettes

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
npx ai-tailwind --help
```

## How It Works

Takes your hex colors and generates a complete Tailwind theme with expanded shades, semantic naming, and proper color relationships.

## License

MIT. Free forever. Use it however you want.
