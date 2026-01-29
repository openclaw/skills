---
name: index-suggester
description: Get smart database index suggestions from query patterns. Use when queries are slow.
---

# Index Suggester

Your queries are slow but you're not sure what to index. This tool analyzes your query files and tells you exactly what indexes to create.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx @lxgicstudios/ai-index ./src/queries/
```

## What It Does

- Analyzes your query files for patterns
- Identifies missing indexes
- Suggests composite indexes for complex queries
- Explains why each index helps

## Usage Examples

```bash
# Analyze all query files
npx @lxgicstudios/ai-index ./src/queries/

# Single file
npx @lxgicstudios/ai-index ./src/queries/users.ts -o indexes.sql

# Prisma queries
npx @lxgicstudios/ai-index ./prisma/
```

## Best Practices

- **Don't over-index** - indexes slow down writes
- **Consider query frequency** - index hot paths first
- **Use composite indexes wisely** - column order matters
- **Test before deploying** - indexes can change query plans

## When to Use This

- Query performance is degrading
- Adding new queries to an app
- Database audit and optimization
- Learning about indexing strategies

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
npx @lxgicstudios/ai-index --help
```

## How It Works

Reads your query files, extracts WHERE clauses and JOIN conditions, then determines what indexes would speed up those queries. The AI considers selectivity and query patterns to prioritize suggestions.

## License

MIT. Free forever. Use it however you want.
