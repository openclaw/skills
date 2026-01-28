---
name: migration-gen
description: Generate SQL migration files from ORM schemas. Use when managing database changes.
---

# Migration Generator

Your ORM schema changed and you need migration files. This tool reads your schema and generates timestamped UP and DOWN migrations.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-migrate --orm prisma --name add_users
```

## What It Does

- Reads Prisma, Drizzle, TypeORM, or Sequelize schemas
- Generates timestamped migration folders
- Creates both UP and DOWN SQL
- Includes proper guards (IF NOT EXISTS, etc.)

## Usage Examples

```bash
# Prisma migration
npx ai-migrate --orm prisma --name add_users

# Drizzle with custom output
npx ai-migrate --orm drizzle --name add_orders --output ./db/migrations

# TypeORM
npx ai-migrate --orm typeorm --name add_products
```

## Best Practices

- **Test migrations locally** - run up and down before deploying
- **Keep them small** - one logical change per migration
- **Version control them** - migrations are code
- **Never edit deployed migrations** - create new ones instead

## When to Use This

- Schema changes need migration files
- Converting ORM operations to raw SQL
- Setting up migration workflow
- Learning proper migration structure

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
npx ai-migrate --help
```

## How It Works

Finds your ORM schema files, parses the model definitions, and generates SQL migration files. Creates timestamped folders with up.sql and down.sql that are safe to run multiple times.

## License

MIT. Free forever. Use it however you want.
