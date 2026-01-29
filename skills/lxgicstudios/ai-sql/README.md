# @lxgicstudios/ai-sql

[![npm version](https://img.shields.io/npm/v/@lxgicstudios/ai-sql.svg)](https://www.npmjs.com/package/@lxgicstudios/ai-sql)
[![npm downloads](https://img.shields.io/npm/dm/@lxgicstudios/ai-sql.svg)](https://www.npmjs.com/package/@lxgicstudios/ai-sql)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered natural language to SQL converter. Just describe what you want.

Convert natural language to SQL queries. Just describe what you want.

## Install

```bash
npm install -g @lxgicstudios/ai-sql
```

## Usage

```bash
npx @lxgicstudios/ai-sql "find users who signed up last week"
npx @lxgicstudios/ai-sql "top 10 products by revenue" -d mysql
npx @lxgicstudios/ai-sql "monthly active users trend" -s "users(id,email,created_at,last_login)"
```

## Options

- `-d, --dialect <dialect>` - SQL dialect (default: PostgreSQL)
- `-s, --schema <schema>` - Table schema for context

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## License

MIT
