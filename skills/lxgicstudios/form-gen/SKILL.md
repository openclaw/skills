---
name: form-gen
description: Generate form components with validation. Use when building forms.
---

# Form Generator

Forms are tedious. Validation is worse. Describe what fields you need and get a complete form component with validation wired up.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx @lxgicstudios/ai-form "signup form with email, password, name"
```

## What It Does

- Generates React form components
- Includes validation with react-hook-form + zod
- Handles error states and accessibility
- Supports TypeScript out of the box

## Usage Examples

```bash
# Signup form
npx @lxgicstudios/ai-form "signup form with email, password, name"

# Checkout form with TypeScript
npx @lxgicstudios/ai-form "checkout form with address and payment" -t

# Contact form to file
npx @lxgicstudios/ai-form "contact form" -o ContactForm.tsx -t
```

## Best Practices

- **Use TypeScript** - catch errors at compile time
- **Show inline errors** - don't wait until submit
- **Add loading states** - show progress during submission
- **Test with keyboard** - forms must be accessible

## When to Use This

- Need a form fast without boilerplate
- Setting up validation patterns
- Prototyping with working forms
- Learning react-hook-form + zod

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Needs OPENAI_API_KEY environment variable.

```bash
npx @lxgicstudios/ai-form --help
```

## How It Works

Takes your form description, determines the fields and their validation rules, then generates a complete React component using react-hook-form for state management and zod for validation schemas.

## License

MIT. Free forever. Use it however you want.
