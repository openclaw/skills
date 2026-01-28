---
name: storybook-gen
description: Generate Storybook stories from React components. Use when documenting components or setting up a design system.
---

# Storybook Generator

Point it at a React component. Get back complete Storybook stories with all the variants, controls, and edge cases. No more writing boilerplate stories by hand.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-storybook ./src/components/Button.tsx
```

## What It Does

- Analyzes component props and generates appropriate controls
- Creates stories for common states (default, disabled, loading, error)
- Handles complex prop types including objects and callbacks
- Generates proper TypeScript types for story args
- Includes realistic example data, not just placeholder text

## Usage Examples

```bash
# Generate stories for a single component
npx ai-storybook ./src/components/Card.tsx

# Process entire components directory
npx ai-storybook ./src/components/ --recursive

# Output CSF3 format
npx ai-storybook ./src/Button.tsx --format csf3

# Include interaction tests
npx ai-storybook ./src/Modal.tsx --with-interactions

# Specify output directory
npx ai-storybook ./src/Input.tsx -o ./stories/
```

## Best Practices

- **Write good prop types first** - Better TypeScript types mean better generated stories
- **Include JSDoc comments** - The AI uses your documentation to create meaningful descriptions
- **Generate, then customize** - Use this for the boilerplate, add your specific edge cases manually
- **Keep components focused** - Components with clear, single responsibilities generate cleaner stories

## When to Use This

- Setting up Storybook for an existing codebase
- Adding a new component and need stories fast
- Documenting a component library for your team
- Creating a design system with consistent story patterns

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
npx ai-storybook --help
```

## How It Works

The tool parses your React component to extract prop types, default values, and component structure. It then generates Storybook stories that exercise each prop combination, creating meaningful examples based on the prop names and types.

## License

MIT. Free forever. Use it however you want.
