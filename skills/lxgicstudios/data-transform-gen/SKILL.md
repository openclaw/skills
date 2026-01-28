---
name: data-transform-gen
description: Generate ETL and data transformation scripts. Use when migrating data between systems.
---

# Data Transform Generator

Moving data between databases or formats requires writing tedious transformation scripts. Describe your source and destination and get a complete ETL script.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-data-transform "CSV to PostgreSQL"
```

## What It Does

- Generates complete data transformation scripts
- Handles schema mapping between different formats
- Supports databases, files, and APIs
- Includes error handling and validation

## Usage Examples

```bash
# File to database
npx ai-data-transform "CSV to PostgreSQL"

# API to database
npx ai-data-transform "JSON API to SQLite"

# Database to database
npx ai-data-transform "MongoDB to Elasticsearch"

# With transformations
npx ai-data-transform "Excel to MySQL, convert dates and normalize names"
```

## Best Practices

- **Validate before loading** - catch bad data early
- **Batch large datasets** - don't load 1M rows at once
- **Log progress** - know where you are if it fails
- **Test on sample data** - verify transforms work before full run

## When to Use This

- Migrating to a new database
- Loading data from external sources
- Building ETL pipelines
- One-time data imports

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
npx ai-data-transform --help
```

## How It Works

Takes your description of source and destination formats, then generates a Node.js script that handles reading, transforming, and writing data. The AI includes proper error handling and progress logging.

## License

MIT. Free forever. Use it however you want.
