# ai-email-template

Generate responsive email templates that work everywhere. HTML, React Email, or MJML.

## Install

```bash
npm install -g ai-email-template
```

## Usage

```bash
npx ai-email-template "welcome email with verify button"
npx ai-email-template "order confirmation with items table" -f react
npx ai-email-template "password reset" -o reset.html
```

## Options

- `-f, --format <format>` - html, react, or mjml (default: html)
- `-o, --output <file>` - Write to file

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## License

MIT
