---
name: notion
description: Work with Notion pages and databases via the official Notion API.
homepage: https://developers.notion.com
metadata:
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - NOTION_API_KEY
    install:
      - id: node
        kind: note
        label: "Requires notion-cli (Node.js) or notion-cli-py (Python). See docs below."
---

# Notion

This skill lets the agent work with **Notion pages and databases** using the official Notion API.

The skill is declarative: it documents **safe, recommended operations** and assumes a local CLI
(`notion-cli`) that actually performs API calls.

## Authentication

- Create a Notion Integration at https://www.notion.so/my-integrations
- Copy the Internal Integration Token.
- Export it as:

```bash
export NOTION_API_KEY=secret_xxx
```

Share the integration with the pages or databases you want to access.
Unshared content is invisible to the API.

## Profiles (personal / work)

You may define multiple profiles (e.g. personal, work) via env or config.

Default profile: personal

Override via:

```bash
export NOTION_PROFILE=work
```

## Pages

**Read page:**

```bash
notion-cli page get <page_id>
```

**Append blocks:**

```bash
notion-cli block append <page_id> --markdown "..."
```

Prefer appending over rewriting content.

**Create page:**

```bash
notion-cli page create --parent <page_id> --title "..."
```

## Databases

**Inspect schema:**

```bash
notion-cli db get <database_id>
```

**Query database:**

```bash
notion-cli db query <database_id> --filter <json> --sort <json>
```

**Create row:**

```bash
notion-cli page create --database <database_id> --props <json>
```

**Update row:**

```bash
notion-cli page update <page_id> --props <json>
```

## Schema changes (advanced)

Always inspect diffs before applying schema changes.

Never modify database schema without explicit confirmation.

Recommended flow:

```bash
notion-cli db schema diff <database_id> --desired <json>
notion-cli db schema apply <database_id> --desired <json>
```

## Safety notes

- Notion API is rate-limited; batch carefully.
- Prefer append and updates over destructive operations.
- IDs are opaque; store them explicitly, do not infer from URLs.
