# ai-migrate

[![npm version](https://img.shields.io/npm/v/ai-migrate.svg)](https://www.npmjs.com/package/ai-migrate)
[![npm downloads](https://img.shields.io/npm/dm/ai-migrate.svg)](https://www.npmjs.com/package/ai-migrate)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

AI-powered database migration generator. Turn ORM schemas into SQL migration files.

Point it at your ORM schema, get SQL migration files. Supports Prisma, Drizzle, TypeORM, and Sequelize.

## Install

```bash
npm install -g ai-migrate
```

## Usage

```bash
npx ai-migrate --orm prisma --name add_users
```

It'll find your schema files automatically, read them, and generate timestamped UP and DOWN migration SQL files.

```bash
npx ai-migrate --orm drizzle --name add_orders --output ./db/migrations
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## Options

- `--orm <type>` - Which ORM you're using (prisma, drizzle, typeorm, sequelize)
- `--name <name>` - Name for this migration
- `-o, --output <dir>` - Where to put the files (default: ./migrations)
- `-d, --dir <dir>` - Project root to scan for schemas (default: current directory)

## Output

Creates a timestamped folder with `up.sql` and `down.sql`:

```
migrations/
  20240115120000_add_users/
    up.sql
    down.sql
```

Both files include proper guards (IF NOT EXISTS, IF EXISTS) so they're safe to run.

## License

MIT
