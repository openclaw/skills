# ai-stash-name

Stop naming stashes "WIP" or leaving them unnamed. Get meaningful stash names from your actual changes.

## Install

```bash
npm install -g ai-stash-name
```

## Usage

```bash
npx ai-stash-name
# → Stashed as: refactor auth middleware error handling

npx ai-stash-name --dry-run
# → Suggested name: add user avatar upload endpoint
```

## Setup

```bash
export OPENAI_API_KEY=sk-...
```

## Options

- `-d, --dry-run` - Show the suggested name without actually stashing

## License

MIT
