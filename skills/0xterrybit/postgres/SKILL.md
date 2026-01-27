---
name: postgres
description: PostgreSQL database management. Run queries, manage schemas, and monitor performance.
metadata: {"clawdbot":{"emoji":"🐘","always":true,"requires":{"bins":["curl","jq"]}}}
---

# PostgreSQL 🐘

PostgreSQL database management.

## Setup

```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/dbname"
```

## Features

- SQL query execution
- Schema management
- Index optimization
- Backup and restore
- Performance monitoring
- Extensions management

## Usage Examples

```
"Show all tables"
"Run query: SELECT * FROM users"
"Create index on email column"
"Show slow queries"
```

## Commands

```bash
psql "$DATABASE_URL" -c "SELECT * FROM users LIMIT 10"
```

## Safety Rules

1. **ALWAYS** confirm before destructive operations
2. **BACKUP** before schema changes
