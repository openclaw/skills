---
name: component-gen
description: Generate React/Vue/Svelte components from descriptions
---

# Component Generator

Describe what you want, get a production-ready component. Supports React, Vue, and Svelte.

## Quick Start

```bash
npx ai-component "A pricing card with monthly/yearly toggle"
```

## What It Does

- Generates full components from descriptions
- Supports React, Vue, and Svelte
- Includes TypeScript types
- Adds proper accessibility
- Includes Tailwind styling

## Usage Examples

```bash
# Generate React component
npx ai-component "user profile card with avatar"

# Specify framework
npx ai-component "dropdown menu" --framework vue

# With specific styling
npx ai-component "modal dialog" --css tailwind
```

## Output Includes

- Component file with proper structure
- TypeScript interfaces
- Default props
- Basic tests scaffold
- Storybook story (optional)

## Requirements

Node.js 18+. OPENAI_API_KEY required.

## License

MIT. Free forever.
