# Craft CLI Skill

Interact with Craft Documents via the `craft` CLI tool. Fast, token-efficient, LLM-ready.

## Installation

The `craft` CLI binary should be installed at `/usr/local/bin/craft`.

If not installed:
```bash
curl -L https://github.com/nerveband/craft-cli/releases/download/v1.0.0/craft-darwin-arm64 -o craft
chmod +x craft
sudo mv craft /usr/local/bin/
```

## Configuration

Two Craft spaces are available:

### wavedepth Space (Business)
```bash
~/clawd/skills/craft-cli/craft config set-api https://connect.craft.do/links/5VruASgpXo0/api/v1
```

### Personal Space
```bash
~/clawd/skills/craft-cli/craft config set-api https://connect.craft.do/links/HHRuPxZZTJ6/api/v1
```

### Quick Switch (Helper Script)
```bash
# Switch to wavedepth space
~/clawd/skills/craft-cli/craft-helper.sh wavedepth

# Switch to personal space
~/clawd/skills/craft-cli/craft-helper.sh personal

# Check current space
~/clawd/skills/craft-cli/craft-helper.sh current
```

**Check current configuration:**
```bash
~/clawd/skills/craft-cli/craft config get-api
```

## Commands

### List Documents
```bash
# JSON format (default - LLM-friendly)
~/clawd/skills/craft-cli/craft list

# Human-readable table
~/clawd/skills/craft-cli/craft list --format table

# Markdown format
~/clawd/skills/craft-cli/craft list --format markdown
```

### Search Documents
```bash
# Search for documents
~/clawd/skills/craft-cli/craft search "query terms"

# With table output
~/clawd/skills/craft-cli/craft search "query" --format table
```

### Get Document
```bash
# Get document by ID (JSON)
~/clawd/skills/craft-cli/craft get <document-id>

# Save to file
~/clawd/skills/craft-cli/craft get <document-id> --output document.md

# Different format
~/clawd/skills/craft-cli/craft get <document-id> --format markdown
```

### Create Document
```bash
# Create with title only
~/clawd/skills/craft-cli/craft create --title "My New Document"

# Create from file
~/clawd/skills/craft-cli/craft create --title "My Document" --file content.md

# Create with inline markdown
~/clawd/skills/craft-cli/craft create --title "Quick Note" --markdown "# Hello\nThis is content"

# Create as child of another document
~/clawd/skills/craft-cli/craft create --title "Child Doc" --parent <parent-id>
```

### Update Document
```bash
# Update title
~/clawd/skills/craft-cli/craft update <document-id> --title "New Title"

# Update from file
~/clawd/skills/craft-cli/craft update <document-id> --file updated-content.md

# Update with inline markdown
~/clawd/skills/craft-cli/craft update <document-id> --markdown "# Updated\nNew content"

# Update both title and content
~/clawd/skills/craft-cli/craft update <document-id> --title "New Title" --file content.md
```

### Delete Document
```bash
~/clawd/skills/craft-cli/craft delete <document-id>
```

### Info Commands
```bash
# Show API info and recent documents
~/clawd/skills/craft-cli/craft info

# List all available documents
~/clawd/skills/craft-cli/craft docs
```

### Version
```bash
~/clawd/skills/craft-cli/craft version
```

## Output Formats

- **json** (default): Machine-readable JSON, ideal for LLMs and scripts
- **table**: Human-readable table format
- **markdown**: Markdown-formatted output

Set default format in config or use `--format` flag per command.

## API URL Override

Override the configured API URL for any command:
```bash
~/clawd/skills/craft-cli/craft list --api-url https://connect.craft.do/links/ANOTHER_LINK/api/v1
```

## Error Handling

The CLI provides clear error messages with exit codes:

- **Exit Code 0**: Success
- **Exit Code 1**: User error (invalid input, missing arguments)
- **Exit Code 2**: API error (server-side issues)
- **Exit Code 3**: Configuration error

Common errors:
- `authentication failed. Check API URL` - Invalid/unauthorized API URL
- `resource not found` - Document ID doesn't exist
- `rate limit exceeded. Retry later` - Too many requests
- `no API URL configured. Run 'craft config set-api <url>' first` - Missing config

## Usage Examples

### Workflow: List and Search
```bash
# List all documents in wavedepth space
~/clawd/skills/craft-cli/craft config set-api https://connect.craft.do/links/5VruASgpXo0/api/v1
~/clawd/skills/craft-cli/craft list --format table

# Search for specific documents
~/clawd/skills/craft-cli/craft search "proposal" --format table
```

### Workflow: Create and Update
```bash
# Create a new document
~/clawd/skills/craft-cli/craft create --title "Project Notes" --markdown "# Initial notes\n\nStart here."

# Get the document ID from output, then update
~/clawd/skills/craft-cli/craft update <doc-id> --title "Updated Project Notes"

# Verify the update
~/clawd/skills/craft-cli/craft get <doc-id> --format markdown
```

### Workflow: Export Document
```bash
# Get a specific document and save to file
~/clawd/skills/craft-cli/craft get <doc-id> --output exported-notes.md
```

### LLM Integration
```bash
# Get all documents as JSON (pipe to processing)
~/clawd/skills/craft-cli/craft list | jq '.[] | {id, title}'

# Search and extract specific fields
~/clawd/skills/craft-cli/craft search "meeting" | jq '.[].title'
```

## Tips

1. **Default to JSON format** for LLM consumption (it's the default)
2. **Use table format** when showing results to humans
3. **Check configuration** before operations: `craft config get-api`
4. **Switch spaces easily** with `craft config set-api <url>`
5. **Override API URL** temporarily with `--api-url` flag instead of changing config

## GitHub Repository

Source code and documentation: https://github.com/nerveband/craft-cli

## Version

Current version: 1.6.0
