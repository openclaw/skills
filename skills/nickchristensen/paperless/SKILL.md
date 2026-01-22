---
name: paperless
description: Interact with Paperless-NGX document management system via ppls CLI. Search, retrieve, upload, and organize documents.
emoji: 📄
metadata: {"clawdbot":{"requires":{"bins":["ppls"]},"install":[{"id":"node","kind":"node","package":"@nickchristensen/ppls","bins":["ppls"],"label":"Install ppls CLI (npm/bun)"}]}}
---

# Paperless-NGX CLI

Search and manage documents in your Paperless-NGX installation using the `ppls` CLI.

## What is Paperless-NGX?

[Paperless-NGX](https://docs.paperless-ngx.com/) is a document management system that scans, OCRs, and organizes your documents. The `ppls` CLI provides command-line access to search, download, upload, and manage your paperless library.

## Setup

Install via npm/bun:

```bash
npm install -g @nickchristensen/ppls
# or
bun add -g @nickchristensen/ppls
```

Configure connection:

```bash
ppls config set hostname http://your-paperless-host
ppls config set token your-api-token
```

Or use environment variables:
```bash
export PPLS_HOSTNAME=http://your-paperless-host
export PPLS_TOKEN=your-api-token
```

## Common Commands

### Search Documents

```bash
# Search by name/title
ppls documents list --name-contains "invoice" --json

# Search by specific IDs
ppls documents list --id-in 1234,5678 --json

# Paginate results
ppls documents list --page 2 --page-size 50 --json

# Sort results
ppls documents list --sort created --json
```

### Get Document Details

```bash
# Show full document metadata (including OCR'd content)
ppls documents show 1234 --json

# Get just the basics
ppls documents show 1234 --plain
```

### Download Documents

```bash
# Download single file
ppls documents download 1234

# Download to path
ppls documents download 1234 --output /tmp/document.pdf

# Download multiple documents
ppls documents download 1234,5678

# Download multiple documents to path
ppls documents download 1234,5678 --output-dir ~/tmp
```

### Upload Documents

```bash
# Upload with metadata
ppls documents add receipt.pdf \
  --title "Store Receipt" \
  --correspondent 5 \
  --document-type 2 \
  --tag 10

# Upload without metadata (will be processed by Paperless)
ppls documents add scan.pdf
```

### Manage Tags

```bash
# List all tags
ppls tags list --json

# Create a new tag
ppls tags add "Tax Documents" --color "#ff0000"

# Search tags by name
ppls tags list --name-contains "tax" --json
```

### Manage Correspondents

```bash
# List all correspondents
ppls correspondents list --json

# Create new correspondent
ppls correspondents add "New Vendor"
```

## Common Use Cases

### "Find documents with 'tax' in the name"

```bash
ppls documents list --name-contains "tax" --json
```

### "Show me all invoices"

```bash
ppls documents list --name-contains "invoice" --json
```

### "Download a specific document"

```bash
ppls documents show 1234 --json  # Get details first
ppls documents download 1234 --output doc.pdf
```

### "Add a scanned receipt with metadata"

```bash
ppls documents add receipt.pdf --title "Grocery Receipt" --tag 25 --correspondent 5
```

### "Search for specific text in OCR'd content"

```bash
# Get all docs, then search the content field
ppls documents list --json | jq '.[] | select(.content | contains("warranty"))'
```

## Output Formats

ppls supports multiple output formats:

- `--json` - Machine-readable JSON (best for scripts/AI)
- `--plain` - Plain text (simple, parseable)
- `--table` - Formatted table (human-readable)

**For AI/automation, always use `--json`**

## Tips

- **JSON output:** Parse with `jq` for complex queries
- **Date format:** Customize with `--date-format` (uses date-fns tokens)
- **Pagination:** Use `--page-size` and `--page` for large result sets
- **IDs:** Most commands accept numeric IDs (tags, correspondents, documents)

## Links

- **ppls GitHub:** https://github.com/NickChristensen/ppls
- **Paperless-NGX Docs:** https://docs.paperless-ngx.com/
