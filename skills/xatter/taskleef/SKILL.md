---
name: taskleef
description: Use when managing todos, tasks, projects, or kanban boards via Taskleef.com. Supports adding, listing, completing, deleting todos, organizing with projects, and managing kanban boards. Use when the user wants to track tasks, manage their todo list, organize work by projects, or use kanban workflows.
metadata: {"clawdbot":{"emoji":"✅","requires":{"bins":["todo","curl","jq"],"env":["TASKLEEF_API_KEY"]},"primaryEnv":"TASKLEEF_API_KEY","homepage":"https://taskleef.com"}}
---

# Taskleef

Manage todos, projects, and kanban boards using the Taskleef CLI. Taskleef.com is a flexible todo application that supports simple task lists, project organization, and kanban board workflows.

## Prerequisites

The `todo` CLI requires:
- `curl` - for making API requests
- `jq` - for parsing JSON responses
- `TASKLEEF_API_KEY` environment variable

## Authentication

The CLI uses the `TASKLEEF_API_KEY` environment variable. Users can get their API key from https://taskleef.com.

Optionally, users can use `--auth-file` flag to specify an auth file:
```bash
todo --auth-file ~/.taskleef.auth list
todo -a ~/.taskleef.auth list
```

## Core Commands

### Todo Management

**List todos:**
```bash
todo list           # List pending todos
todo ls             # Alias for list
todo list -a        # List all todos including completed
```

**Add todos:**
```bash
todo add "Buy groceries"
todo "Buy groceries"    # Quick add without 'add' keyword
```

**Show todo details:**
```bash
todo show <title-or-id>
```

**Complete todos:**
```bash
todo complete <title-or-id>
todo done <title-or-id>
```

**Delete todos:**
```bash
todo delete <title-or-id>
todo rm <title-or-id>
```

**View inbox:**
```bash
todo inbox    # List todos not assigned to any project
```

### Subtasks

**Add subtasks:**
```bash
todo subtask <parent-title-or-id> "Subtask title"
```

### Projects

**List projects:**
```bash
todo project list
```

**Create project:**
```bash
todo project add "Project Name"
```

**Show project details:**
```bash
todo project show <project-name-or-id>
```

**Delete project:**
```bash
todo project delete <project-name-or-id>
```

**Add todo to project:**
```bash
todo project add-todo <project-name-or-id> <todo-title-or-id>
```

**Remove todo from project:**
```bash
todo project remove-todo <project-name-or-id> <todo-title-or-id>
```

### Kanban Boards

**Show board:**
```bash
todo board                           # Show default board (ASCII view)
todo board show <board-name-or-id>   # Show specific board
```

**List boards:**
```bash
todo board list
```

**List column cards:**
```bash
todo board column <column-name-or-id>
```

**Move card:**
```bash
todo board move <card-title-or-id> <column-name-or-id>
```

**Mark card done:**
```bash
todo board done <card-title-or-id>
```

**Assign card:**
```bash
todo board assign <card-title-or-id>
```

**Clear column:**
```bash
todo board clear <column-name-or-id>
```

## Identifier Matching

Commands accept:
- **ID prefix**: First few characters of UUID (e.g., `abc12`)
- **Title match**: Partial, case-insensitive title match (e.g., `groceries` matches "Buy groceries")

## Priority Indicators

When listing todos, you'll see:
- ○ No priority
- ● (green) Low priority
- ● (yellow) Medium priority
- ● (red) High priority

## Usage Tips

1. **Finding items**: You can reference todos, projects, boards, columns, and cards by partial title or ID prefix
2. **Quick workflow**: Use `todo "task"` for fast task entry
3. **Project organization**: Group related todos under projects for better organization
4. **Kanban boards**: Use boards for visual workflow management
5. **Subtasks**: Break down complex tasks into subtasks for better tracking

## Examples

```bash
# Add and complete a todo
todo add "Review pull request"
todo done "pull request"

# Create a project and add todos
todo project add "Website Redesign"
todo project add-todo "Website" "Fix login"

# View kanban board and move cards
todo board
todo board move "Feature A" "Done"
```

## Error Handling

If the `TASKLEEF_API_KEY` is not set or invalid, commands will fail. Ensure the API key is configured before running commands.

## Additional Resources

- Website: https://taskleef.com
- Generate API key: https://taskleef.com (user dashboard)