---
name: reflect
description: Append to daily notes and create notes in Reflect. Use for capturing thoughts, todos, or syncing information to your knowledge graph.
homepage: https://reflect.app
---

# Reflect Notes Skill

Reflect is a networked note-taking app. Notes are E2E encrypted, so the API is **append-only** — we can write but not read note contents.

## Setup

1. Create OAuth credentials at https://reflect.app/developer/oauth
2. Generate an access token from that interface
3. Set environment variables:
   ```bash
   export REFLECT_TOKEN="your-access-token"
   export REFLECT_GRAPH_ID="your-graph-id"  # Find via: curl -H "Authorization: Bearer $REFLECT_TOKEN" https://reflect.app/api/graphs
   ```

Or store in 1Password and update `scripts/reflect.sh` with your vault/item path.

## What We Can Do

1. **Append to daily notes** — Add items to today's note (or a specific date)
2. **Create new notes** — Create standalone notes with subject + markdown content
3. **Create links** — Save bookmarks with highlights
4. **Get links/books** — Retrieve saved links and books

## API Reference

Base URL: `https://reflect.app/api`
Auth: `Authorization: Bearer <access_token>`

### Append to Daily Note

```bash
curl -X PUT "https://reflect.app/api/graphs/$REFLECT_GRAPH_ID/daily-notes" \
  -H "Authorization: Bearer $REFLECT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here",
    "transform_type": "list-append",
    "date": "2026-01-25",          # optional, defaults to today
    "list_name": "[[List Name]]"   # optional, append to specific list
  }'
```

### Create a Note

```bash
curl -X POST "https://reflect.app/api/graphs/$REFLECT_GRAPH_ID/notes" \
  -H "Authorization: Bearer $REFLECT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Note Title",
    "content_markdown": "# Heading\n\nContent here...",
    "pinned": false
  }'
```

### Create a Link

```bash
curl -X POST "https://reflect.app/api/graphs/$REFLECT_GRAPH_ID/links" \
  -H "Authorization: Bearer $REFLECT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "title": "Page Title",
    "description": "Optional description",
    "highlights": ["Quote 1", "Quote 2"]
  }'
```

### Get Links

```bash
curl "https://reflect.app/api/graphs/$REFLECT_GRAPH_ID/links" \
  -H "Authorization: Bearer $REFLECT_TOKEN"
```

## Helper Script

Use `scripts/reflect.sh` for common operations:

```bash
# Append to daily note
./scripts/reflect.sh daily "Remember to review PR #6"

# Append to specific list in daily note  
./scripts/reflect.sh daily "Buy milk" "[[Shopping]]"

# Create a new note
./scripts/reflect.sh note "Meeting Notes" "# Standup\n\n- Discussed X\n- Action item: Y"

# Save a link
./scripts/reflect.sh link "https://example.com" "Example Site" "Great resource"
```

## Use Cases

- **Capture todos** from chat → append to daily note
- **Save interesting links** mentioned in conversation
- **Create meeting notes** or summaries
- **Sync reminders** to Reflect for persistence
- **Backlink to lists** like `[[Ideas]]` or `[[Project Name]]`

## Limitations

- **Cannot read note contents** (E2E encrypted)
- **Append-only** — can't edit or delete existing content
- **No search** — can't query existing notes
