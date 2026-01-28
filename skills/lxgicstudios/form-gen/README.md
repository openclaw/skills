# @lxgicstudios/ai-form

Generate form components with validation from plain English descriptions.

## Install

```bash
npm install -g @lxgicstudios/ai-form
```

## Usage

```bash
npx @lxgicstudios/ai-form "signup form with email, password, name"
npx @lxgicstudios/ai-form "checkout form with address and payment" -t
npx @lxgicstudios/ai-form "contact form" -o ContactForm.tsx -t
```

## Options

- `-t, --typescript` - Generate TypeScript
- `-l, --library <lib>` - Validation library (default: react-hook-form + zod)
- `-o, --output <file>` - Write to file

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## License

MIT
