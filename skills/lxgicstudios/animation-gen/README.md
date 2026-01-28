# ai-animation

Generate CSS and Framer Motion animations from plain English.

## Install

```bash
npm install -g ai-animation
```

## Usage

```bash
npx ai-animation "fade in from left with bounce"
npx ai-animation "pulse glow effect" -f css
npx ai-animation "staggered list entrance" -f framer -o animations.ts
```

## Options

- `-f, --format <format>` - css, framer, or both (default: both)
- `-o, --output <file>` - Write to file

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## License

MIT
