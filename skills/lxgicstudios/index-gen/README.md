# @lxgicstudios/ai-index

Analyze your query patterns and get smart database index suggestions. Tells you exactly what to create and why.

## Install

```bash
npm install -g @lxgicstudios/ai-index
```

## Usage

```bash
npx @lxgicstudios/ai-index ./src/queries/
# Analyzes all query files and suggests indexes

npx @lxgicstudios/ai-index ./src/queries/users.ts -o indexes.sql
# Single file, saves SQL to file
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## Options

- `-o, --output <path>` - Save suggestions to file

## License

MIT
