---
name: obsidian-daily
description: Manage Obsidian Daily Notes via obsidian-cli. Create and open daily notes, append entries (journals, logs, tasks), read past notes by date, and search vault content. Handles relative dates like "yesterday", "last Friday", "3 days ago".
compatibility: Requires obsidian-cli installed via Homebrew (Mac/Linux)
metadata: {"clawdbot":{"requires":{"bins":["obsidian-cli"]},"install":[{"id":"brew","kind":"brew","formula":"yakitrak/yakitrak/obsidian-cli","bins":["obsidian-cli"],"label":"Install obsidian-cli (brew)"}]}}
---

# Obsidian Daily Notes

Interact with Obsidian Daily Notes: create notes, append entries, read by date, and search content.

## Setup

Check if a default vault is configured:

```bash
obsidian-cli print-default --path-only 2>/dev/null && echo "OK" || echo "NOT_SET"
```

If `NOT_SET`, ask the user:
1. **Vault name** (required)
2. **Daily notes folder** (default: vault root, common: `Daily Notes`, `Journal`, `daily`)
3. **Date format** (default: `YYYY-MM-DD`)

Configure the vault:

```bash
obsidian-cli set-default "VAULT_NAME"
```

**Obsidian Daily Notes plugin defaults:**
- Date format: `YYYY-MM-DD`
- New file location: Vault root
- Template file location: (none)

## Date Handling

Get current date:

```bash
date +%Y-%m-%d
```

Cross-platform relative dates (GNU first, BSD fallback):

| Reference | Command |
|-----------|---------|
| Today | `date +%Y-%m-%d` |
| Yesterday | `date -d yesterday +%Y-%m-%d 2>/dev/null \|\| date -v-1d +%Y-%m-%d` |
| Last Friday | `date -d "last friday" +%Y-%m-%d 2>/dev/null \|\| date -v-friday +%Y-%m-%d` |
| 3 days ago | `date -d "3 days ago" +%Y-%m-%d 2>/dev/null \|\| date -v-3d +%Y-%m-%d` |
| Next Monday | `date -d "next monday" +%Y-%m-%d 2>/dev/null \|\| date -v+monday +%Y-%m-%d` |

## Commands

### Open/Create Today's Note

```bash
obsidian-cli daily
```

Opens today's daily note in Obsidian, creating it from template if it doesn't exist.

### Append Entry

Add a timestamped entry to today's note:

```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n---\n\n**%s**\n\n%s\n' "$(date +%H:%M)" "ENTRY_TEXT")" --append
```

With custom folder:

```bash
obsidian-cli daily && obsidian-cli create "Daily Notes/$(date +%Y-%m-%d).md" --content "$(printf '\n---\n\n**%s**\n\n%s\n' "$(date +%H:%M)" "ENTRY_TEXT")" --append
```

### Read Note

Today:

```bash
obsidian-cli print "$(date +%Y-%m-%d).md"
```

Specific date:

```bash
obsidian-cli print "2025-01-10.md"
```

Relative date (yesterday):

```bash
obsidian-cli print "$(date -d yesterday +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d).md"
```

### Search Content

```bash
obsidian-cli search-content "TERM"
```

### Search Notes

Interactive fuzzy finder:

```bash
obsidian-cli search
```

### Specific Vault

Add `--vault "NAME"` to any command:

```bash
obsidian-cli print "2025-01-10.md" --vault "Work"
```

## Use Cases

**Journal entry:**
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n---\n\n**%s**\n\n%s\n' "$(date +%H:%M)" "Reflected on the team meeting. Good progress on Q1 goals.")" --append
```

**Task/To-do:**
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n---\n\n**%s**\n\n%s\n' "$(date +%H:%M)" "- [ ] Review PR #42\n- [ ] Send weekly report")" --append
```

**Log/Note:**
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n---\n\n**%s**\n\n%s\n' "$(date +%H:%M)" "Bug found: auth token expiring early. See #123")" --append
```

**Read last Friday:**
```bash
obsidian-cli print "$(date -d 'last friday' +%Y-%m-%d 2>/dev/null || date -v-friday +%Y-%m-%d).md"
```

**Find all mentions of "meeting":**
```bash
obsidian-cli search-content "meeting"
```

## Entry Format

Each appended entry:

```markdown
---

**HH:MM**

Your content here
```

The horizontal rule separates entries. Adjust format based on user preference.

