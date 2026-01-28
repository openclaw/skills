---
name: gno
description: Search local documents, files, notes, and knowledge bases. Index directories, search with BM25/vector/hybrid, get AI answers with citations. Use when user wants to search files, find documents, query notes, look up information in local folders, index a directory, set up document search, build a knowledge base, needs RAG/semantic search, or wants to start a local web UI for their docs.
allowed-tools: Bash(gno:*) Read
---

# GNO - Local Knowledge Engine

Fast local semantic search. Index once, search instantly. No cloud, no API keys.

## When to Use This Skill

- User asks to **search files, documents, or notes**
- User wants to **find information** in local folders
- User needs to **index a directory** for searching
- User mentions **PDFs, markdown, Word docs, code** to search
- User asks about **knowledge base** or **RAG** setup
- User wants **semantic/vector search** over their files
- User needs to **set up MCP** for document access
- User wants a **web UI** to browse/search documents
- User asks to **get AI answers** from their documents
- User wants to **tag, categorize, or filter** documents
- User asks about **backlinks, wiki links, or related notes**
- User wants to **visualize document connections** or see a **knowledge graph**

## Quick Start

```bash
gno init                              # Initialize in current directory
gno collection add ~/docs --name docs # Add folder to index
gno index                             # Build index (ingest + embed)
gno search "your query"               # BM25 keyword search
```

## Command Overview

| Category     | Commands                                                         | Description                                               |
| ------------ | ---------------------------------------------------------------- | --------------------------------------------------------- |
| **Search**   | `search`, `vsearch`, `query`, `ask`                              | Find documents by keywords, meaning, or get AI answers    |
| **Links**    | `links`, `backlinks`, `similar`, `graph`                         | Navigate document relationships and visualize connections |
| **Retrieve** | `get`, `multi-get`, `ls`                                         | Fetch document content by URI or ID                       |
| **Index**    | `init`, `collection add/list/remove`, `index`, `update`, `embed` | Set up and maintain document index                        |
| **Tags**     | `tags`, `tags add`, `tags rm`                                    | Organize and filter documents                             |
| **Context**  | `context add/list/rm/check`                                      | Add hints to improve search relevance                     |
| **Models**   | `models list/use/pull/clear/path`                                | Manage local AI models                                    |
| **Serve**    | `serve`                                                          | Web UI for browsing and searching                         |
| **MCP**      | `mcp`, `mcp install/uninstall/status`                            | AI assistant integration                                  |
| **Skill**    | `skill install/uninstall/show/paths`                             | Install skill for AI agents                               |
| **Admin**    | `status`, `doctor`, `cleanup`, `reset`, `vec`, `completion`      | Maintenance and diagnostics                               |

## Search Modes

| Command                | Speed   | Best For                           |
| ---------------------- | ------- | ---------------------------------- |
| `gno search`           | instant | Exact keyword matching             |
| `gno vsearch`          | ~0.5s   | Finding similar concepts           |
| `gno query --fast`     | ~0.7s   | Quick lookups                      |
| `gno query`            | ~2-3s   | Balanced (default)                 |
| `gno query --thorough` | ~5-8s   | Best recall, complex queries       |
| `gno ask --answer`     | ~3-5s   | AI-generated answer with citations |

**Retry strategy**: Use default first. If no results: rephrase query, then try `--thorough`.

## Common Flags

```
-n <num>              Max results (default: 5)
-c, --collection      Filter to collection
--tags-any <t1,t2>    Has ANY of these tags
--tags-all <t1,t2>    Has ALL of these tags
--json                JSON output
--files               URI list output
--line-numbers        Include line numbers
```

## Global Flags

```
--index <name>    Alternate index (default: "default")
--config <path>   Override config file
--verbose         Verbose logging
--json            JSON output
--yes             Non-interactive mode
--offline         Use cached models only
--no-color        Disable colors
--no-pager        Disable paging
```

## Important: Embedding After Changes

If you edit/create files that should be searchable via vector search:

```bash
gno index              # Full re-index (sync + embed)
# or
gno embed              # Embed only (if already synced)
```

MCP `gno.sync` and `gno.capture` do NOT auto-embed. Use CLI for embedding.

## Reference Documentation

| Topic                                                 | File                                 |
| ----------------------------------------------------- | ------------------------------------ |
| Complete CLI reference (all commands, options, flags) | [cli-reference.md](cli-reference.md) |
| MCP server setup and tools                            | [mcp-reference.md](mcp-reference.md) |
| Usage examples and patterns                           | [examples.md](examples.md)           |
