---
name: qmd
description: Fast local search for markdown files, notes, and docs using qmd CLI. Use instead of `find` for file discovery. Combines BM25 full-text search, vector semantic search, and LLM reranking—all running locally. Use when searching for files, finding code, locating documentation, or discovering content in indexed collections.
---

# qmd — Fast Local Markdown Search

## When to Use

- **Finding files** — use instead of `find` across large directories (avoids hangs)
- **Searching notes/docs** — semantic or keyword search in indexed collections
- **Code discovery** — find implementations, configs, or patterns
- **Context gathering** — pull relevant snippets before answering questions

## Quick Reference

### Search (most common)

```bash
# Keyword search (BM25)
qmd search "alpaca API" -c projects

# Semantic search (understands meaning)
qmd vsearch "how to implement stop loss"

# Combined search with reranking (best quality)
qmd query "trading rules for breakouts"

# File paths only (fast discovery)
qmd search "config" --files -c kell

# Full document content
qmd search "pattern detection" --full --line-numbers
```

### Collections

```bash
# List collections
qmd collection list

# Add new collection
qmd collection add /path/to/folder --name myproject --mask "*.md,*.py"

# Re-index after changes
qmd update
```

### Get Files

```bash
# Get full file
qmd get myproject/README.md

# Get specific lines
qmd get myproject/config.py:50 -l 30

# Get multiple files by glob
qmd multi-get "*.yaml" -l 50 --max-bytes 10240
```

### Output Formats

- `--files` — paths + scores (for file discovery)
- `--json` — structured with snippets
- `--md` — markdown formatted
- `-n 10` — limit results

## Tips

1. **Always use collections** (`-c name`) to scope searches
2. **Run `qmd update`** after adding new files
3. **Use `qmd embed`** to enable vector search (one-time, takes a few minutes)
4. **Prefer `qmd search --files`** over `find` for large directories

## Models (auto-downloaded)

- Embedding: embeddinggemma-300M
- Reranking: qwen3-reranker-0.6b
- Generation: Qwen3-0.6B

All run locally — no API keys needed.
