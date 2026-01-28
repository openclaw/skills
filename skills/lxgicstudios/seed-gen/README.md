# ai-seed

Generate realistic database seed data from your schema. Works with Prisma, SQL, Drizzle, TypeORM, and more.

## Install

```bash
npm install -g ai-seed
```

## Usage

```bash
npx ai-seed ./prisma/schema.prisma
# Generates seed script with 10 records per table

npx ai-seed ./prisma/schema.prisma -n 50
# 50 records per table

npx ai-seed ./schema.sql -o seed.ts
# SQL schema, saves to file
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## Options

- `-n, --count <number>` - Records per table (default: 10)
- `-o, --output <path>` - Save to file

## License

MIT
