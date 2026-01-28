---
name: theme-gen
description: Generate a complete design system from brand colors using AI. Use when starting a new project or standardizing colors.
---

# Theme Generator

Give it your brand colors. Get back a complete design system with semantic tokens, shade scales, and ready-to-use CSS variables or Tailwind config. Stop manually picking 9 shades of blue.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-theme --primary "#3B82F6" --secondary "#10B981"
```

## What It Does

- Generates full color shade scales from your base colors (50 through 950)
- Creates semantic tokens like success, warning, error, info
- Outputs CSS custom properties, Tailwind config, or both
- Ensures accessible contrast ratios between foreground and background
- Builds consistent spacing and typography scales

## Usage Examples

```bash
# Generate from primary color only
npx ai-theme --primary "#6366F1"

# Full brand palette
npx ai-theme --primary "#3B82F6" --secondary "#10B981" --accent "#F59E0B"

# Output Tailwind config
npx ai-theme --primary "#8B5CF6" --format tailwind

# Include dark mode variants
npx ai-theme --primary "#EC4899" --dark-mode

# Export to file
npx ai-theme --primary "#14B8A6" -o ./theme.css
```

## Best Practices

- **Start with your hero color** - The primary color sets the tone. Get that right first
- **Don't fight the generated scales** - They're mathematically balanced. Trust the output
- **Test in context** - Paste the variables into your project and see how they look on real UI
- **Customize after generating** - Use this as a starting point, then tweak individual shades

## When to Use This

- Starting a new project and need a color system fast
- Client gave you one brand color and expects a full palette
- Converting a messy codebase to consistent design tokens
- Exploring color options during early design phases

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
npx ai-theme --help
```

## How It Works

The tool takes your base colors and uses color theory principles to generate harmonious shade scales. It calculates luminance values to ensure each step in the scale has proper contrast, then maps these to semantic purposes like backgrounds, text, and interactive states.

## License

MIT. Free forever. Use it however you want.
