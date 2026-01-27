---
name: bring-add
description: Use when user wants to add items to Bring! shopping lists. For adding single items, batch items, or items from stdin/files. Supports dry-run preview and JSON output.
---

# Bring! Add Items CLI

## Overview

CLI for adding items to Bring! shopping lists. Supports quick single-item mode, batch mode, stdin/pipe input, and interactive mode.

## When to Use

**Use this skill when:**
- User wants to add items to a Bring! shopping list
- Adding single item with optional specification (e.g., "Milk 1L")
- Adding multiple items at once (batch mode)
- Piping items from a file or other command
- Need to preview additions with dry-run
- Need JSON output for scripting

**Don't use when:**
- User wants to browse recipes (use bring-recipes instead)
- User wants to remove items from a list
- User wants to view current list contents

## Quick Reference

| Command | Purpose |
|---------|---------|
| `bring-add "Item" "spec"` | Add single item with specification |
| `bring-add --batch "A, B 1L, C"` | Add multiple comma-separated items |
| `bring-add -` | Read items from stdin |
| `bring-add` | Interactive mode (TTY only) |
| `bring-add lists` | Show available shopping lists |
| `bring-add --dry-run ...` | Preview without modifying |

**Environment variables:**
```bash
export BRING_EMAIL="your@email.com"
export BRING_PASSWORD="yourpassword"
export BRING_DEFAULT_LIST="Shopping"  # optional
```

## Installation

```bash
cd skills/bring-add
npm install
```

## Common Workflows

**Add a single item:**
```bash
node index.js "Tomatoes" "500g"
node index.js "Milk"
```

**Add to specific list:**
```bash
node index.js --list "Party" "Chips" "3 bags"
```

**Batch add multiple items:**
```bash
node index.js --batch "Tomatoes 500g, Onions, Cheese 200g"
```

**Pipe from file:**
```bash
cat shopping-list.txt | node index.js -
echo -e "Milk 1L\nBread\nButter" | node index.js -
```

**Preview before adding:**
```bash
node index.js --dry-run --batch "Apples 1kg, Pears"
```

**Get JSON output:**
```bash
node index.js --json --batch "Milk, Bread" 2>/dev/null
```

**List available lists:**
```bash
node index.js lists
node index.js --json lists
```

## Flags Reference

| Flag | Description |
|------|-------------|
| `-l, --list <name>` | Target list (name or UUID) |
| `-b, --batch <items>` | Comma-separated items |
| `-n, --dry-run` | Preview without modifying |
| `-q, --quiet` | Suppress non-error output |
| `-v, --verbose` | Show detailed progress |
| `--json` | Output JSON to stdout |
| `--no-color` | Disable colored output |
| `--no-input` | Never prompt; fail if input required |

## Input Format

Items follow the pattern: `ItemName [Specification]`

| Input | Item | Spec |
|-------|------|------|
| `Tomatoes 500g` | Tomatoes | 500g |
| `Oat milk 1L` | Oat milk | 1L |
| `Red onions 3` | Red onions | 3 |
| `Cheese` | Cheese | (empty) |

Rule: Last word becomes specification if it contains a number or unit (g, kg, L, ml, Stück, pck).

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Generic failure (API error, network) |
| `2` | Invalid usage (bad args, missing input) |
| `3` | Authentication failed |
| `4` | List not found |
| `130` | Interrupted (Ctrl-C) |

## Common Mistakes

**Forgetting environment variables:**
Set `BRING_EMAIL` and `BRING_PASSWORD` before running.

**Wrong list name:**
Use `bring-add lists` to see available lists and their exact names.

**Specification parsing:**
The last word is treated as specification only if it looks like a quantity. "Red onions" stays as one item, but "Red onions 3" splits into item "Red onions" with spec "3".

**Interactive mode in scripts:**
Use `--no-input` flag in scripts to fail explicitly rather than hang waiting for input.

## Implementation Notes

- Uses `node-bring-api` with `batchUpdateList()` API
- Requires Node.js 18.0.0+
- Outputs data to stdout, progress/errors to stderr
- JSON mode available for automation
- Interactive mode only when stdin is a TTY
