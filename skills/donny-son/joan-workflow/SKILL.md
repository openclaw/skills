---
name: Joan Workflow
description: This skill should be used when the user asks about "joan", "pods", "workspace", "domain knowledge", "context sync", "joan init", "joan todo", or needs guidance on how Joan's knowledge management system works. Provides workflow guidance for pods, todos, plans, and workspace management.
version: 0.1.0
---

# Joan Workflow

Joan is a workspace-based knowledge and task management system for AI-assisted development. This skill covers when and how to use Joan's core concepts.

## Core Concepts

### Workspaces

Workspaces are the top-level organizational unit in Joan. Each workspace contains:
- **Pods**: Versioned domain knowledge documents
- **Todos**: Tasks scoped to the workspace
- **Plans**: Implementation specs linked to todos
- **Members**: Team members with roles (admin, member)

### Pods

Pods are versioned markdown documents containing domain knowledge. Use pods to:
- Document project architecture and design decisions
- Store domain-specific terminology and business rules
- Share knowledge across team members and AI assistants
- Maintain living documentation that evolves with the project

**Pod lifecycle:**
1. Create locally with `joan pod create`
2. Edit the markdown file in `.joan/pods/`
3. Push to server with `joan pod push`
4. Pull latest with `joan pod pull`

### Todos

Todos are tasks scoped to a workspace. Use todos to:
- Track work items across team members
- Assign tasks and set priorities
- Link implementation plans to tasks

**Todo workflow:**
1. Create with `joan todo create`
2. List with `joan todo list`
3. Update status as work progresses
4. Archive when complete

### Plans

Plans are implementation specs linked to todos. Use plans to:
- Document how a feature will be implemented
- Break down complex tasks into steps
- Share implementation approach with team

## CLI Commands Reference

### Project Initialization

```bash
joan init                    # Interactive workspace selection
joan init -w <workspace-id>  # Non-interactive with specific workspace
joan status                  # Show project and auth status
```

### Pod Management

```bash
joan pod list               # List tracked pods
joan pod list --all         # List all workspace pods
joan pod add                # Add workspace pods to project
joan pod create             # Create new pod locally
joan pod pull               # Pull pods from server
joan pod push               # Push local pods to server
joan pod open               # Open pod in browser
```

### Todo Management

```bash
joan todo list              # List todos for tracked pods
joan todo list --mine       # List todos assigned to me
joan todo create            # Create new todo
joan todo update <id>       # Update todo fields
joan todo archive <id>      # Archive completed todo
```

### Plan Management

```bash
joan plan list <todo-id>    # List plans for a todo
joan plan create <todo-id>  # Create implementation plan
joan plan pull <todo-id>    # Pull plans from server
joan plan push <todo-id>    # Push plans to server
```

### Context Generation

```bash
joan context claude         # Generate CLAUDE.md with Joan context
```

## When to Use What

### Starting a New Project

1. Run `joan init` to connect project to a workspace
2. Select pods relevant to the project domain
3. Run `joan context claude` to inject context into CLAUDE.md
4. Read the generated pod references before coding

### Before Coding a Feature

1. Check if relevant pods exist: `joan pod list --all`
2. Add any missing pods: `joan pod add`
3. Pull latest: `joan pod pull`
4. Read pods to understand domain context

### After Completing Work

1. Consider if learnings should become a pod
2. Update or create todos to reflect progress
3. Push any local changes: `joan pod push` and `joan todo push`

### Documenting New Knowledge

1. Create a pod: `joan pod create`
2. Write domain knowledge in markdown
3. Push to share: `joan pod push`
4. Update CLAUDE.md context: `joan context claude`

## MCP Integration

Joan provides an MCP server at `https://joan.land/mcp/joan` with tools:
- `list_workspaces` - List accessible workspaces
- `list_pods` - List pods in a workspace
- `get_pod` - Retrieve pod content

The MCP server uses OAuth 2.1 authentication. Authenticate via the CLI first with `joan auth login`.

## Project Configuration

Joan stores project config in `.joan/config.yaml`:

```yaml
workspace_id: <uuid>
tracked_pods:
  - name: "Pod Name"
    id: <uuid>
```

Pods are stored locally in `.joan/pods/` as markdown files.

## Best Practices

### Pod Authoring

- Use clear, descriptive titles
- Include context about when the knowledge applies
- Keep pods focused on a single domain concept
- Update pods when knowledge evolves
- Reference related pods when helpful

### Todo Management

- Create todos at the right granularity (not too big, not too small)
- Link todos to relevant pods for context
- Update status promptly to keep team informed
- Archive completed todos to reduce noise

### Context Synchronization

- Run `joan context claude` after changing tracked pods
- Pull pods before starting significant work
- Push changes promptly to share with team
