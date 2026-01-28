---
name: cover-letter-gen
description: Generate tailored cover letters with AI. Use when applying for jobs.
---

# Cover Letter Generator

Cover letters are tedious to write and most people just recycle the same one. This tool generates tailored cover letters that actually match the role you're applying for.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-cover-letter "frontend role at Stripe"
```

## What It Does

- Generates professional cover letters tailored to the role
- Matches tone to company culture
- Highlights relevant skills for the position
- Avoids generic filler content

## Usage Examples

```bash
# Frontend role
npx ai-cover-letter "frontend role at Stripe"

# Senior position
npx ai-cover-letter "senior backend engineer at Vercel"

# Startup vs enterprise
npx ai-cover-letter "ML engineer at early stage AI startup"

# Save to file
npx ai-cover-letter "devops engineer at Netflix" -o cover-letter.md
```

## Best Practices

- **Be specific about the role** - include company name and position
- **Add your context** - mention your years of experience and key skills
- **Review and personalize** - add specific details about why this company
- **Keep it concise** - nobody reads a 3 page cover letter

## When to Use This

- Applying to jobs and dreading the cover letter
- Need a good starting point to customize
- Want to match your tone to company culture
- Batch applying and need variations

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
npx ai-cover-letter --help
```

## How It Works

Takes your description of the role and company, generates a cover letter that highlights relevant skills and matches the expected tone. The AI understands different company cultures and adjusts the formality accordingly.

## License

MIT. Free forever. Use it however you want.
