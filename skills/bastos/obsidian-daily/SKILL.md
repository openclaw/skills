---
name: obsidian-daily
description: Manage Obsidian Daily Notes via obsidian-cli. Create and open daily notes, append entries (journals, logs, tasks, links), read past notes by date, and search vault content. Handles relative dates like "yesterday", "last Friday", "3 days ago". Requires obsidian-cli installed via Homebrew (Mac/Linux) or Scoop (Windows).
license: MIT
metadata:
  author: github.com/bastos
  version: "2.0"
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

```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "ENTRY_TEXT")" --append
```

With custom folder:

```bash
obsidian-cli daily && obsidian-cli create "Daily Notes/$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "ENTRY_TEXT")" --append
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

## Example Output

```markdown
- Went to the doctor
- [ ] Buy groceries
- https://github.com/anthropics/skills
- 15:45 This is a log line
```

## Use Cases

**Journal entry:**
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "- Went to the doctor")" --append
```

**Task:**
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "- [ ] Buy groceries")" --append
```

**Link:**
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "- https://github.com/anthropics/skills")" --append
```

**Timestamped log:**
```bash
obsidian-cli daily && obsidian-cli create "$(date +%Y-%m-%d).md" --content "$(printf '\n%s' "- $(date +%H:%M) This is a log line")" --append
```

**Read last Friday:**
```bash
obsidian-cli print "$(date -d 'last friday' +%Y-%m-%d 2>/dev/null || date -v-friday +%Y-%m-%d).md"
```

**Search for "meeting":**
```bash
obsidian-cli search-content "meeting"
```
