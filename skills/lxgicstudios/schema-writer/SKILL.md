---
name: schema-writer
description: Generate database schemas from plain English. Use when you need SQL tables fast.
---

# Schema Writer

Designing database tables by hand is tedious. You know what columns you need, you know the relationships, but writing out CREATE TABLE statements with proper types, constraints, and indexes takes forever. Describe your data model in plain English and this tool writes the SQL for you. Supports PostgreSQL, MySQL, and SQLite.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-schema "users with email, name, and posts with title and body"
```

## What It Does

- Turns plain English descriptions into proper SQL schema definitions
- Generates CREATE TABLE statements with appropriate data types and constraints
- Supports PostgreSQL, MySQL, and SQLite dialects
- Handles relationships, foreign keys, and indexes automatically
- Writes output to a file or prints to stdout

## Usage Examples

```bash
# Generate PostgreSQL schema (default)
npx ai-schema "e-commerce with users, products, orders, and reviews"

# Generate MySQL schema
npx ai-schema "blog with authors and posts" --dialect mysql

# Save schema to a file
npx ai-schema "task management app" --dialect sqlite -o schema.sql
```

## Best Practices

- **Be specific about relationships** - Saying "users have many posts" gives better results than just listing both tables. The more detail you give, the better the foreign keys and indexes.
- **Specify your dialect** - PostgreSQL is the default, but if you're using MySQL or SQLite, set the flag. Data types differ between databases and getting the wrong ones is annoying.
- **Review constraints** - The tool adds sensible defaults for NOT NULL and unique constraints, but your business logic might need different rules. Always check.
- **Use it as scaffolding** - The generated schema is a solid starting point. Add your own indexes, triggers, and custom types on top of it.

## When to Use This

- Starting a new project and need a database schema quickly
- Prototyping an idea and want to skip the SQL boilerplate
- Teaching someone database design with concrete examples
- Converting a data model from a whiteboard sketch to actual SQL

## How It Works

The tool takes your plain English description and sends it to an AI model that understands database design patterns. It generates properly typed SQL with relationships, constraints, and indexes based on the dialect you choose.

## Requirements

No install needed. Just run with npx. Node.js 18+ recommended.

```bash
npx ai-schema --help
```

## Part of the LXGIC Dev Toolkit

This is one of 110+ free developer tools built by LXGIC Studios. No paywalls, no sign-ups, no API keys on free tiers. Just tools that work.

**Find more:**
- GitHub: https://github.com/LXGIC-Studios
- Twitter: https://x.com/lxgicstudios
- Substack: https://lxgicstudios.substack.com
- Website: https://lxgic.dev

## License

MIT. Free forever. Use it however you want.