---
name: landing-gen
description: Generate a beautiful HTML landing page from your package.json. Use when you need a quick marketing page for your project.
---

# Landing Page Generator

You just shipped a package. Now you need a landing page but don't want to spend two hours messing with HTML and CSS. This tool reads your package.json and spits out a complete, good looking landing page in one command. No templates to configure, no design decisions to make.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-landing .
```

## What It Does

- Reads your package.json and pulls out the name, description, features, and repo links
- Generates a fully styled HTML landing page with hero section, feature grid, and CTA
- Outputs a single landing.html file you can deploy anywhere
- Handles responsive design automatically so it looks good on mobile
- Includes proper meta tags and semantic HTML out of the box

## Usage Examples

```bash
# Generate from current directory
npx ai-landing .

# Generate from a specific project
npx ai-landing ~/projects/my-cool-lib

# Custom output file
npx ai-landing . -o index.html
```

## Best Practices

- **Write a good package.json description first** - The better your description, the better the landing page copy will be
- **Add keywords to package.json** - They get used as feature highlights on the page
- **Deploy to GitHub Pages** - The output is a single HTML file, perfect for gh-pages
- **Tweak the output** - Use it as a starting point, then customize colors and copy to match your brand

## When to Use This

- You just published an npm package and need a landing page fast
- You want a quick demo page for a hackathon project
- You need a placeholder site while you build the real one
- Your open source project needs a better first impression than a GitHub README

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended.

```bash
npx ai-landing --help
```

## How It Works

The tool parses your package.json to extract project metadata. It then sends that info to an AI model that generates clean, semantic HTML with inline styles. The result is a single file landing page that you can open in any browser or deploy to any static host.

## License

MIT. Free forever. Use it however you want.