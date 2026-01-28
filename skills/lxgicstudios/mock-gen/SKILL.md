---
name: mock-gen
description: Generate realistic mock data from descriptions, types, or schemas. Use when you need test data fast.
---

# Mock Gen

Every developer has been there. You need test data and you end up writing the same boring JSON by hand or copying from some random Stack Overflow answer. This tool generates realistic mock data from plain English descriptions, TypeScript types, or JSON schemas. Tell it what you want, how many records, and what format. Done.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-mock-data "e-commerce users with name, email, address, and order history"
```

## What It Does

- Generates realistic mock data from plain English descriptions
- Supports TypeScript types and JSON schemas as input
- Outputs in JSON, CSV, or SQL insert format
- Configurable record count (default 10)
- Can write directly to a file with the --output flag

## Usage Examples

```bash
# Generate 10 user records as JSON
npx ai-mock-data "users with name, email, and signup date"

# Generate 50 product records as CSV
npx ai-mock-data "products with SKU, name, price, and category" -c 50 -f csv

# Generate from a TypeScript type file and save to disk
npx ai-mock-data "fill this schema" -s ./types/User.ts -o mock-users.json
```

## Best Practices

- **Be specific in descriptions** - "users with realistic US addresses" gets better results than just "users"
- **Use schemas for consistency** - If you have TypeScript types, pass them with --schema for exact field matching
- **Start small then scale** - Generate 5 records first to check quality, then bump to 100+
- **Pick the right format** - Use CSV for spreadsheets, SQL for database seeding, JSON for API mocking

## When to Use This

- Setting up a dev database and need seed data
- Building a frontend prototype and need realistic API responses
- Writing tests that need varied, realistic input data
- Demoing a product and need good-looking sample data

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
npx ai-mock-data --help
```

## How It Works

The tool takes your description or schema file and sends it to an AI model that understands data structures. It generates realistic, varied records that match your spec. The output gets formatted as JSON, CSV, or SQL inserts depending on what you pick.

## License

MIT. Free forever. Use it however you want.