---
name: context7
description: Up-to-date library documentation via Context7 MCP. No API key required. Use for finding code examples, API docs, and version-specific documentation for any library.
metadata: {"clawdbot":{"emoji":"📚","requires":{"bins":["jq","curl"]}}}
---

# Context7 - Library Documentation (MCP)

CLI wrapper for Context7's hosted MCP endpoint. No API key required.

> **Note:** Examples show command syntax. Replace library names and queries with the user's actual request.

## Resolve Library ID

Find the Context7 library ID for a package:

```bash
bash scripts/context7 resolve "<library-name>"
```

Returns matching libraries with their IDs (e.g., `/vercel/next.js`, `/tanstack/query`).

## Query Documentation

Get documentation for a specific library:

```bash
bash scripts/context7 docs "<library-id>" "<query>"
```

Options:
- `-n, --num`: Max tokens to return (default: 10000)

## Workflow

1. First resolve the library name to get its ID:
   ```bash
   context7 resolve "react query"
   ```

2. Then query the docs using the ID:
   ```bash
   context7 docs /tanstack/query "useQuery mutation"
   ```

## Command Reference

| Command | Description |
|---------|-------------|
| `context7 resolve "<name>"` | Find library ID |
| `context7 docs "<id>" "<query>"` | Query library documentation |

## Notes

- Uses Context7's hosted MCP endpoint (`https://mcp.context7.com/mcp`)
- No API key required
- Library IDs use format `/org/project` (e.g., `/vercel/next.js`)
- Requires `jq` and `curl`
