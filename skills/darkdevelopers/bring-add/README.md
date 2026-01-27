# bring-add

Add items to Bring! shopping lists from the command line.

## Installation

```bash
cd /path/to/node-bring-api/skills/bring-add
npm install
```

## Quick Start

```bash
# Set credentials
export BRING_EMAIL="your@email.com"
export BRING_PASSWORD="yourpassword"
export BRING_DEFAULT_LIST="Shopping"  # optional

# Add a single item
node index.js "Tomatoes" "500g"
```

## Usage

```
bring-add [global flags] [item] [spec]
bring-add [global flags] <subcommand>
```

### Quick Mode (single item)

```bash
node index.js "Tomatoes" "500g"
node index.js "Milk"
node index.js --list "Party" "Chips" "3 bags"
```

### Batch Mode (multiple items)

```bash
node index.js --batch "Tomatoes 500g, Onions, Cheese 200g"
```

### Stdin Mode

```bash
echo -e "Milk 1L\nBread\nButter" | node index.js -
cat shopping-list.txt | node index.js -
```

### Interactive Mode

```bash
node index.js
```

When stdin is a TTY and no arguments are provided, enters interactive mode:

```
Adding to list: Shopping

Enter items (empty line to finish):
> Tomatoes 500g
> Onions
> Cheese 200g
>

Added 3 items to "Shopping"
```

### List Shopping Lists

```bash
node index.js lists
node index.js -v lists          # show UUIDs
node index.js --json lists      # JSON output
```

## Global Flags

| Flag | Description |
|------|-------------|
| `-h, --help` | Show help and exit |
| `-V, --version` | Print version and exit |
| `-l, --list <name>` | Target list (name or UUID) |
| `-b, --batch <items>` | Comma-separated items |
| `-n, --dry-run` | Preview without modifying |
| `-q, --quiet` | Suppress non-error output |
| `-v, --verbose` | Show detailed progress |
| `--json` | Output JSON to stdout |
| `--no-color` | Disable colors |
| `--no-input` | Never prompt; fail if input required |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BRING_EMAIL` | Yes | Bring! account email |
| `BRING_PASSWORD` | Yes | Bring! account password |
| `BRING_DEFAULT_LIST` | No | Default list name or UUID |
| `NO_COLOR` | No | Disable colors (any value) |
| `DEBUG` | No | Show debug output |

**Precedence:** Flags > Environment > Defaults

## Input Format

`ItemName [Specification]`

| Input | Item | Spec |
|-------|------|------|
| `Tomatoes 500g` | Tomatoes | 500g |
| `Oat milk 1L` | Oat milk | 1L |
| `Red onions 3` | Red onions | 3 |
| `Cheese` | Cheese | (empty) |

Rule: Last word is specification if it contains a number or unit.

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Generic failure (API error, network) |
| `2` | Invalid usage (bad args, missing input) |
| `3` | Authentication failed |
| `4` | List not found |
| `130` | Interrupted (Ctrl-C) |

## I/O Contract

| Stream | Content |
|--------|---------|
| **stdout** | Data: JSON output, dry-run preview |
| **stderr** | Progress, prompts, errors, warnings |

## JSON Output

### Add Result

```json
{
  "list": {
    "name": "Shopping",
    "uuid": "a5a22d4b-..."
  },
  "added": [
    {"item": "Tomatoes", "spec": "500g"},
    {"item": "Cheese", "spec": ""}
  ],
  "count": 2
}
```

### Dry-Run Result

```json
{
  "list": {"name": "Shopping", "uuid": "..."},
  "wouldAdd": [...],
  "count": 2,
  "dryRun": true
}
```

### Lists Result

```json
{
  "lists": [
    {"name": "Shopping", "uuid": "...", "isDefault": true},
    {"name": "Home", "uuid": "...", "isDefault": false}
  ]
}
```

## Examples

```bash
# Quick add
node index.js "Milk" "1L"

# Batch add
node index.js --batch "Bread, Butter, Eggs 6"

# Preview without adding
node index.js --dry-run --batch "Apples 1kg, Pears"

# Add to specific list
node index.js --list "Party" "Chips"

# Pipe from file
cat list.txt | node index.js -

# JSON output for scripting
node index.js --json --batch "Milk, Bread" 2>/dev/null | jq '.count'

# Silent mode
node index.js -q "Milk" && echo "OK"

# List available lists as JSON
node index.js --json lists

# Verbose mode with UUIDs
node index.js -v lists
```

## License

MIT
