---
name: supabase-rls-gen
description: Generate Supabase RLS policies from Prisma schema. Use when securing database.
---

# Supabase RLS Generator

Row Level Security is powerful but the policy syntax is tricky. This reads your schema and generates proper RLS policies.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-supabase-gen ./prisma/schema.prisma
```

## What It Does

- Reads your Prisma schema
- Generates Supabase RLS policies
- Handles common patterns (own data, team access)
- Includes policy enable statements

## Usage Examples

```bash
# Generate from Prisma
npx ai-supabase-gen ./prisma/schema.prisma
```

## Best Practices

- **Enable RLS** - it's off by default
- **Test policies** - verify they work as expected
- **Use helper functions** - auth.uid(), auth.role()
- **Think about all operations** - SELECT, INSERT, UPDATE, DELETE

## When to Use This

- Setting up Supabase security
- Adding RLS to existing tables
- Learning RLS patterns
- Securing multi-tenant apps

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
npx ai-supabase-gen --help
```

## How It Works

Parses your Prisma schema to understand data models and relationships. Then generates appropriate RLS policies based on common access patterns.

## License

MIT. Free forever. Use it however you want.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/supabase-schema-gen](https://github.com/lxgicstudios/supabase-schema-gen)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
