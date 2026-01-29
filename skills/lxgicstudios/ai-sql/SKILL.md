---
name: sql-gen
description: Generate SQL queries from natural language
---

# SQL Generator

Describe what you want, get the SQL. Works with any database.

## Quick Start

```bash
npx ai-sql "get all users who signed up this month and made a purchase"
```

## What It Does

- Converts English to SQL
- Handles complex JOINs
- Adds proper WHERE clauses
- Optimizes for performance

## Usage Examples

```bash
# Generate query
npx ai-sql "top 10 products by revenue last quarter"

# With schema context
npx ai-sql "users without orders" --schema ./schema.sql

# Specific dialect
npx ai-sql "monthly active users" --dialect postgres
```

## Dialects Supported

- PostgreSQL
- MySQL
- SQLite
- SQL Server
- Oracle

## Output Example

```sql
SELECT u.id, u.email, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY u.id, u.email
HAVING COUNT(o.id) > 0;
```

## Requirements

Node.js 18+. OPENAI_API_KEY required.

## License

MIT. Free forever.

---

**Built by LXGIC Studios**

- GitHub: [github.com/lxgicstudios/ai-sql](https://github.com/lxgicstudios/ai-sql)
- Twitter: [@lxgicstudios](https://x.com/lxgicstudios)
