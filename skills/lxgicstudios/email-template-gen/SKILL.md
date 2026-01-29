---
name: email-template-gen
description: Generate responsive email templates. Use when building transactional emails.
---

# Email Template Generator

Email HTML is stuck in 1999. Tables, inline styles, outlook hacks. Describe what you want and get a template that actually works everywhere.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-email-template "welcome email with verify button"
```

## What It Does

- Generates responsive email templates
- Works in Gmail, Outlook, Apple Mail, and more
- Supports HTML, React Email, and MJML
- Includes dark mode support

## Usage Examples

```bash
# Welcome email
npx ai-email-template "welcome email with verify button"

# Order confirmation
npx ai-email-template "order confirmation with items table" -f react

# Password reset
npx ai-email-template "password reset" -o reset.html

# Newsletter
npx ai-email-template "weekly newsletter with header and article cards"
```

## Best Practices

- **Test in Litmus or Email on Acid** - every client is different
- **Keep it simple** - complex layouts break in Outlook
- **Use web fonts sparingly** - many clients ignore them
- **Always include plain text** - some people prefer it

## When to Use This

- Building transactional email system
- Creating marketing email templates
- Updating legacy email templates
- Need a starting point for React Email

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgicstudios.com

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Needs OPENAI_API_KEY environment variable.

```bash
npx ai-email-template --help
```

## How It Works

Takes your description and generates email templates using table-based layouts that work across email clients. For React Email format, it generates proper components. For MJML, it generates the markup that compiles to email-safe HTML.

## License

MIT. Free forever. Use it however you want.
