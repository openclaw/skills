# ai-merge-resolve

Stop manually resolving merge conflicts. Let AI figure out the best merge.

## Install

```bash
npm install -g ai-merge-resolve
```

## Usage

```bash
npx ai-merge-resolve conflicted-file.ts
# Prints resolved content

npx ai-merge-resolve conflicted-file.ts --write
# Writes resolved content back to file

cat conflicted-file.ts | npx ai-merge-resolve
# Read from stdin
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## Options

- `-w, --write` - Write resolved content back to the file

## License

MIT
