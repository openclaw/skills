---
name: seed-gen
description: Generate realistic database seed data from your schema. Use when you need test data that looks real.
---

# Seed Gen

Fake data that looks real. No more "test user 1" and "lorem ipsum" everywhere. This tool reads your schema and generates seed data that actually makes sense. Real names, realistic emails, proper timestamps, coherent relationships.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-seed prisma/schema.prisma
```

## What It Does

- Generates realistic seed data based on your schema
- Understands field types and generates appropriate values
- Maintains referential integrity across related tables
- Creates data that tells a coherent story (not random garbage)
- Outputs ready-to-use seed scripts

## Usage Examples

```bash
# Generate seed data from schema
npx ai-seed prisma/schema.prisma

# Specify number of records
npx ai-seed prisma/schema.prisma --count 50

# Target specific tables
npx ai-seed prisma/schema.prisma --tables users,posts,comments

# Output as SQL
npx ai-seed prisma/schema.prisma --format sql > seed.sql
```

## Best Practices

- **Match your use case** - E-commerce app? Ask for product-focused data. Social app? User interactions.
- **Start small** - Generate 10-20 records first to check quality before scaling up
- **Check relationships** - Make sure foreign keys point to existing records
- **Add edge cases** - Ask for some empty fields, deleted users, old dates to test your UI

## When to Use This

- Starting a new project and need demo data
- Building UI and need realistic content to design around
- Testing queries and need enough data to see performance issues
- Demoing to stakeholders and want it to look professional

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended. Requires OPENAI_API_KEY environment variable.

```bash
export OPENAI_API_KEY=sk-...
npx ai-seed --help
```

## How It Works

Reads your schema to understand models and relationships. Uses GPT to generate contextually appropriate data that fits your domain. Outputs seed scripts with proper insert order to respect foreign key constraints.

## License

MIT. Free forever. Use it however you want.
