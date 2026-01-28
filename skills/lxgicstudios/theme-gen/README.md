# ai-theme

Generate a complete design system from your brand colors. Gets you a full color palette, typography scale, spacing, shadows, and more.

## Install

```bash
npm install -g ai-theme
```

## Usage

```bash
npx ai-theme "#FF4500" "#1A1A2E"
# Generates CSS custom properties

npx ai-theme "#FF4500" "#1A1A2E" -f tailwind
# Generates tailwind.config.js theme extension

npx ai-theme "#FF4500" "#1A1A2E" -f json -o tokens.json
# Saves design tokens as JSON
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## Options

- `-f, --format <type>` - Output format: css, tailwind, json (default: css)
- `-o, --output <path>` - Save to file

## License

MIT
