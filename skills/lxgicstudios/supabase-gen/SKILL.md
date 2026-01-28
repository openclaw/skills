---
name: supabase-gen
description: Generate Supabase RLS policies from Prisma schema. Use when setting up row-level security for your tables.
---

# Supabase Gen

Row-level security is a pain to write. This tool reads your Prisma schema and generates proper RLS policies for Supabase. You get secure defaults that actually make sense for your data model.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-supabase-gen prisma/schema.prisma
```

## What It Does

- Reads your Prisma schema and understands the data model
- Generates RLS policies for SELECT, INSERT, UPDATE, DELETE
- Creates auth.uid() checks for user-owned resources
- Handles multi-tenant patterns with organization scoping
- Outputs SQL ready to run in Supabase SQL editor

## Usage Examples

```bash
# Generate RLS from your schema
npx ai-supabase-gen prisma/schema.prisma

# Save to migration file
npx ai-supabase-gen prisma/schema.prisma > supabase/migrations/001_rls.sql

# Specify output format
npx ai-supabase-gen prisma/schema.prisma --format sql
```

## Best Practices

- **Review every policy** - AI gets close but you know your access patterns best
- **Test with different users** - RLS bugs are sneaky. Test reads and writes as different roles.
- **Start restrictive** - Better to block legitimate access than leak data. Loosen later.
- **Use service role sparingly** - Service role bypasses RLS. That's powerful and dangerous.

## When to Use This

- Setting up a new Supabase project with existing Prisma schema
- Adding RLS to tables that currently have none
- Auditing your security and want a fresh set of policies to compare
- Learning RLS patterns and want to see how they should look

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
npx ai-supabase-gen --help
```

## How It Works

Parses your Prisma schema to understand models, relations, and field types. Then generates appropriate RLS policies based on common patterns like user ownership, org membership, and public/private access. Uses GPT to handle edge cases intelligently.

## License

MIT. Free forever. Use it however you want.
