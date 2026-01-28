---
name: sql-injection-scanner
description: Detect SQL injection vulnerabilities in your codebase. Use when you need to find unsafe database queries before they get exploited.
---

# SQL Injection Scanner

SQL injection has been around for decades and it's still in the OWASP Top 10. This tool scans your backend code for unsafe query construction, string concatenation in SQL, and missing parameterized queries. It finds the vulnerabilities and shows you how to fix them.

**One command. Zero config. Just works.**

## Quick Start

```bash
npx ai-sql-check src/
```

## What It Does

- Scans your codebase for SQL injection vulnerability patterns
- Detects string concatenation in SQL queries
- Finds missing parameterized query usage
- Identifies unsafe ORM patterns and raw query calls
- Generates fix suggestions showing proper parameterized versions

## Usage Examples

```bash
# Scan your entire backend
npx ai-sql-check src/

# Check a specific API route
npx ai-sql-check src/routes/users.ts

# Scan all database related files
npx ai-sql-check "src/**/*.{ts,js}"
```

## Best Practices

- **Always use parameterized queries** - String concatenation in SQL is never safe, even if you think the input is trusted
- **Check ORM raw query calls** - ORMs are generally safe, but raw query methods bypass protections
- **Scan before every release** - New code means new potential injection points
- **Don't trust input validation alone** - Parameterization is the real defense. Validation is just a bonus.

## When to Use This

- Before a security audit or penetration test
- After adding new database queries to your backend
- When onboarding a legacy codebase with unknown security posture
- As part of your CI security pipeline

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
npx ai-sql-check --help
```

## How It Works

The tool scans your source files for SQL query patterns and analyzes how user input flows into database calls. It uses pattern matching and AI analysis to detect string concatenation, template literals in queries, and unsafe ORM usage. Each finding includes severity, the vulnerable code, and a parameterized query fix.

## License

MIT. Free forever. Use it however you want.