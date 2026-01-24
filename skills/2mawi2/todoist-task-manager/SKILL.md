---
name: todoist
description: Manage Todoist tasks via the `todoist` CLI (list, add, modify, complete, delete). Supports filters, projects, labels, and priorities.
homepage: https://github.com/sachaos/todoist
metadata: {"clawdbot":{"emoji":"✅","requires":{"bins":["todoist"]},"install":[{"id":"brew","kind":"brew","formula":"todoist-cli","bins":["todoist"],"label":"Install todoist-cli via Homebrew"}]}}
---

# Todoist CLI

Use `todoist` to manage Todoist tasks directly from the terminal.

## Setup

1. Install: `brew install todoist-cli`
2. Get your API token from https://app.todoist.com/app/settings/integrations/developer
3. Create config:
```bash
mkdir -p ~/.config/todoist
echo '{"token": "YOUR_API_TOKEN"}' > ~/.config/todoist/config.json
```
4. Sync: `todoist sync`

## List Tasks

```bash
todoist list                           # All tasks
todoist list --filter "today"          # Due today
todoist list --filter "overdue"        # Overdue tasks
todoist list --filter "p1"             # Priority 1 (highest)
todoist list --filter "tomorrow"       # Due tomorrow
todoist list --filter "@work"          # By label
todoist list --filter "#Project"       # By project
todoist list --filter "(today | overdue) & p1"  # Combined filters
```

## Add Tasks

```bash
todoist add "Buy milk"                                    # Simple task
todoist add "Call mom" --priority 1                       # With priority (1=highest, 4=lowest)
todoist add "Meeting" --date "tomorrow 3pm"               # With due date
todoist add "Report" --project-name "Work"                # To specific project
todoist add "Review" --label-names "urgent,review"        # With labels
todoist quick "Buy eggs tomorrow p1 #Shopping @errands"   # Natural language
```

## Modify Tasks

```bash
todoist modify TASK_ID --content "New title"
todoist modify TASK_ID --priority 2
todoist modify TASK_ID --date "next monday"
```

## Complete Tasks

```bash
todoist close TASK_ID              # Complete a task
todoist close TASK_ID TASK_ID2     # Complete multiple tasks
```

## Delete Tasks

```bash
todoist delete TASK_ID
```

## View Details

```bash
todoist show TASK_ID               # Show task details
todoist projects                   # List all projects
todoist labels                     # List all labels
```

## Sync

```bash
todoist sync                       # Sync local cache with Todoist
```

## Output Formats

```bash
todoist list --csv                 # CSV output for scripting
todoist list --color               # Colorized output
todoist list --namespace           # Show parent tasks as namespace
todoist list --indent              # Indent subtasks
```

## Filter Syntax

Todoist CLI supports the [official Todoist filter syntax](https://todoist.com/help/articles/introduction-to-filters-V98wIH):

| Filter | Description |
|--------|-------------|
| `today` | Due today |
| `tomorrow` | Due tomorrow |
| `overdue` | Past due date |
| `no date` | No due date |
| `p1`, `p2`, `p3`, `p4` | Priority level |
| `@label` | By label |
| `#Project` | By project |
| `assigned to: me` | Assigned to you |
| `7 days` | Due in next 7 days |

Combine with `&` (and), `|` (or), `!` (not):
```bash
todoist list --filter "(today | overdue) & p1"
todoist list --filter "#Work & !@done"
```

## Notes

- Run `todoist sync` after making changes in the web/mobile app
- Task IDs are numeric (e.g., `12345678`)
- Config stored in `~/.config/todoist/config.json`
- Cache stored in `~/.config/todoist/cache.json`
