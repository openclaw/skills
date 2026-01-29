# ai-css-to-tailwind

Convert any CSS file to Tailwind utility classes. Get a clean mapping of your existing styles to Tailwind equivalents.

## Install

```bash
npm install -g ai-css-to-tailwind
```

## Usage

```bash
npx ai-css-to-tailwind ./styles.css
# Prints Tailwind class mappings

npx ai-css-to-tailwind ./styles.css -o tailwind-mapping.md
# Saves mapping to a file
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## Options

- `-o, --output <path>` - Save output to a file

## License

MIT
