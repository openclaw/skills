---
name: animation-gen
description: Generate CSS and Framer Motion animations from plain English. Use when you need smooth animations without the math.
---

# Animation Generator

Describing animations is easy. Writing the keyframes and easing functions is not. Tell this tool what you want to see and it'll give you the CSS or Framer Motion code to make it happen.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-animation "fade in from left with bounce"
```

## What It Does

- Converts plain English descriptions to actual animation code
- Supports CSS keyframes and Framer Motion variants
- Handles complex multi-step animations
- Outputs production-ready code you can drop in

## Usage Examples

```bash
# Get CSS keyframes
npx ai-animation "pulse glow effect" -f css

# Get Framer Motion variant
npx ai-animation "staggered list entrance" -f framer

# Save to file
npx ai-animation "smooth slide up reveal" -f both -o animations.ts

# Complex animation
npx ai-animation "shake horizontally three times then settle"
```

## Best Practices

- **Be descriptive** - "bounce twice then fade" beats "make it move"
- **Mention timing** - include "slow", "fast", "0.5s" if timing matters
- **Specify direction** - "from left", "upward", "diagonal" helps a lot
- **Test on device** - animations feel different on mobile

## When to Use This

- Building landing pages and need attention-grabbing effects
- Adding micro-interactions to your UI
- You can picture the animation but can't write the math
- Prototyping quickly before fine-tuning manually

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
npx ai-animation --help
```

## How It Works

Takes your natural language description and translates it into animation primitives. The AI understands common animation terms like "bounce", "ease", "stagger" and converts them to proper timing functions and keyframe values.

## License

MIT. Free forever. Use it however you want.
