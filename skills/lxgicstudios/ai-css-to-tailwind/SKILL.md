---
name: css-to-tailwind
description: Convert CSS files to Tailwind utility classes
---

# CSS to Tailwind

Got legacy CSS? Convert it to Tailwind classes. Handles complex selectors and media queries.

## Quick Start

```bash
npx ai-css-to-tailwind ./src/styles/button.css
```

## What It Does

- Converts CSS rules to Tailwind utilities
- Handles responsive breakpoints
- Converts custom properties to theme values
- Preserves complex hover/focus states

## Usage Examples

```bash
# Convert a CSS file
npx ai-css-to-tailwind ./styles/header.css

# Convert and update component
npx ai-css-to-tailwind ./styles/card.css --update ./components/Card.tsx

# Batch convert
npx ai-css-to-tailwind ./styles/*.css
```

## What It Handles

- Media queries → responsive prefixes
- Pseudo-classes → state variants
- CSS variables → theme tokens
- Complex selectors → component patterns

## Requirements

Node.js 18+. OPENAI_API_KEY required.

## License

MIT. Free forever.
