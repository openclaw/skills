---
name: todoist
description: Manage Todoist tasks, projects, labels, and comments via the todoist CLI wrapper. Use when a user asks to add tasks, list todos, complete items, manage projects, or interact with their Todoist account.
---

# Todoist CLI

Manage Todoist via the REST API v2.

## Setup

1. Get API token: Todoist → Settings → Integrations → Developer → API token
2. Set environment variable:
   ```bash
   export TODOIST_API_TOKEN="your_token_here"
   ```
3. Make CLI executable:
   ```bash
   chmod +x ~/clawd/skills/todoist/scripts/todoist
   ```

## CLI Location

```bash
~/clawd/skills/todoist/scripts/todoist
```

## Quick Reference

### Tasks

```bash
# List all tasks
todoist tasks

# List with filter
todoist tasks --filter "today"
todoist tasks --filter "overdue"
todoist tasks --filter "#Work"
todoist tasks --project PROJECT_ID

# Quick views
todoist today
todoist overdue
todoist upcoming

# Get single task
todoist task TASK_ID

# Add task
todoist add "Buy groceries"
todoist add "Call mom" --due tomorrow
todoist add "Meeting prep" --due "today 3pm" --priority 4
todoist add "Review PR" --project PROJECT_ID --labels "work,urgent"
todoist add "Write docs" --description "Include examples"

# Update task
todoist update TASK_ID --content "New title"
todoist update TASK_ID --due "next monday"
todoist update TASK_ID --priority 3

# Complete / reopen / delete
todoist complete TASK_ID
todoist reopen TASK_ID
todoist delete-task TASK_ID
```

### Projects

```bash
# List projects
todoist projects

# Get project
todoist project PROJECT_ID

# Create project
todoist add-project "Work"
todoist add-project "Personal" --color blue --favorite

# Update project
todoist update-project PROJECT_ID --name "New Name"
todoist update-project PROJECT_ID --color red

# Delete project
todoist delete-project PROJECT_ID
```

### Sections

```bash
# List sections
todoist sections
todoist sections PROJECT_ID

# Create section
todoist add-section --name "In Progress" --project PROJECT_ID

# Delete section
todoist delete-section SECTION_ID
```

### Labels

```bash
# List labels
todoist labels

# Create label
todoist add-label "urgent"
todoist add-label "blocked" --color red

# Delete label
todoist delete-label LABEL_ID
```

### Comments

```bash
# List comments
todoist comments --task TASK_ID
todoist comments --project PROJECT_ID

# Add comment
todoist add-comment "Need more info" --task TASK_ID

# Delete comment
todoist delete-comment COMMENT_ID
```

## Filter Syntax

Todoist supports powerful filter queries:

| Filter | Description |
|--------|-------------|
| `today` | Due today |
| `tomorrow` | Due tomorrow |
| `overdue` | Past due |
| `7 days` | Due in next 7 days |
| `no date` | No due date |
| `#ProjectName` | In specific project |
| `@label` | Has label |
| `p1`, `p2`, `p3`, `p4` | Priority level |
| `assigned to: me` | Assigned to you |
| `created: today` | Created today |

Combine with `&` (and) or `|` (or):
```bash
todoist tasks --filter "today & #Work"
todoist tasks --filter "overdue | p1"
```

## Due Date Strings

Natural language due dates:
- `today`, `tomorrow`, `yesterday`
- `next monday`, `next week`
- `in 3 days`
- `every day`, `every weekday`
- `every monday at 9am`
- `Jan 15`, `2026-01-20`
- `today at 3pm`

## Priority Levels

| Value | Meaning |
|-------|---------|
| 1 | Normal (default) |
| 2 | Medium |
| 3 | High |
| 4 | Urgent |

## Output

All commands return JSON. Pipe to `jq` for formatting:

```bash
todoist tasks | jq '.[] | {id, content, due: .due.string}'
todoist today | jq -r '.[].content'
```

## Notes

- Requires `curl` and `jq`
- All output is JSON for easy scripting
- Task IDs are numeric strings (e.g., "8765432109")
- Project IDs are also numeric strings
