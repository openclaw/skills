---
name: api-docs-gen
description: Generate API documentation from route files. Use when you need markdown or OpenAPI specs fast.
---

# API Docs Generator

Your API has 50 endpoints and zero documentation. This tool reads your route files and generates proper docs, either markdown for humans or OpenAPI specs for tools.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-api-docs ./src/routes/
```

## What It Does

- Scans your route files and extracts endpoint information
- Generates clean markdown documentation
- Outputs OpenAPI 3.0 specs for Swagger and other tools
- Documents request/response shapes automatically

## Usage Examples

```bash
# Generate markdown docs
npx ai-api-docs ./src/routes/
# → API_DOCS.md

# Generate OpenAPI spec
npx ai-api-docs ./src/routes/ --format openapi -o spec.yaml

# Custom output path
npx ai-api-docs ./src/api/ -o docs/api.md

# Scan multiple directories
npx ai-api-docs ./routes ./handlers
```

## Best Practices

- **Keep routes organized** - cleaner code means better docs
- **Use TypeScript** - type info improves generated descriptions
- **Review and edit** - AI gets structure right, you add context
- **Regenerate on changes** - make it part of your CI

## When to Use This

- You inherited a codebase with no API docs
- Shipping an MVP and docs are the last thing on your list
- Need to generate Swagger UI quickly
- Onboarding new developers to your API

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
npx ai-api-docs --help
```

## How It Works

Parses your route files to extract HTTP methods, paths, and handler code. Then uses GPT-4o-mini to infer request/response shapes, add descriptions, and format everything according to markdown or OpenAPI standards.

## License

MIT. Free forever. Use it however you want.
