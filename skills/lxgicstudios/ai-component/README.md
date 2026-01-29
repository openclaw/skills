# ai-component

[![npm version](https://img.shields.io/npm/v/ai-component.svg)](https://www.npmjs.com/package/ai-component)
[![npm downloads](https://img.shields.io/npm/dm/ai-component.svg)](https://www.npmjs.com/package/ai-component)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered React component generator. Describe what you want in plain English, get production-ready code.

Generate React components from plain English. Describe what you want, get production-ready code.

## Install

```bash
npm install -g ai-component
```

## Usage

```bash
npx ai-component "pricing card with monthly/yearly toggle"
npx ai-component "navbar with dropdown menu" --typescript --tailwind
npx ai-component "image carousel with dots" -o Carousel.tsx -t
```

## Options

- `-t, --typescript` - Generate TSX instead of JSX
- `--tailwind` - Use Tailwind CSS classes
- `-o, --output <file>` - Write to file

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## License

MIT
