---
name: linear
description: Manage Linear projects, issues, and tasks via the Linear API. Use when you need to create, update, search, or manage Linear issues, projects, teams, milestones, comments, or labels. Supports all Linear operations including project management, issue tracking, task assignment, state transitions, and collaboration workflows.
---

# Linear Project Management

Manage Linear projects, issues, and workflows using the official Linear SDK.

## Quick Start

All commands use `skills/linear/scripts/linear-cli.js`:

```bash
node skills/linear/scripts/linear-cli.js <command> [args]
```

## Core Commands

### Teams & Projects

**List teams:**
```bash
node skills/linear/scripts/linear-cli.js teams
```

**List projects:**
```bash
node skills/linear/scripts/linear-cli.js projects
```

**Create project:**
```bash
node skills/linear/scripts/linear-cli.js createProject "Project Name" "Description" "teamId1,teamId2"
```

### Issues

**List issues:**
```bash
node skills/linear/scripts/linear-cli.js issues
# With filter:
node skills/linear/scripts/linear-cli.js issues '{"state":{"name":{"eq":"In Progress"}}}'
```

**Get issue details:**
```bash
node skills/linear/scripts/linear-cli.js issue ENG-123
```

**Create issue:**
```bash
node skills/linear/scripts/linear-cli.js createIssue "Title" "Description" "teamId"
# With options (priority, projectId, assigneeId, etc.):
node skills/linear/scripts/linear-cli.js createIssue "Title" "Description" "teamId" '{"priority":2,"projectId":"project-id"}'
```

**Update issue:**
```bash
node skills/linear/scripts/linear-cli.js updateIssue "issueId" '{"stateId":"state-id","priority":1}'
```

### Comments

**Add comment:**
```bash
node skills/linear/scripts/linear-cli.js createComment "issueId" "Comment text"
```

### States & Labels

**Get team states:**
```bash
node skills/linear/scripts/linear-cli.js states "teamId"
```

**Get team labels:**
```bash
node skills/linear/scripts/linear-cli.js labels "teamId"
```

### User Info

**Get current user:**
```bash
node skills/linear/scripts/linear-cli.js user
```

## References

- **API.md**: Priority levels, filter examples, and common workflows
- Read when you need examples of complex filters or workflow patterns

## Common Workflows

### Create task for a specific project

1. Get your team ID: `node skills/linear/scripts/linear-cli.js teams`
2. Get your project ID: `node skills/linear/scripts/linear-cli.js projects`
3. Create issue with the IDs:

```bash
node skills/linear/scripts/linear-cli.js createIssue "Implement login" "Add OAuth login flow" "your-team-id" '{"projectId":"your-project-id","priority":2}'
```

### Move issue to different state

1. Get states: `node skills/linear/scripts/linear-cli.js states "teamId"`
2. Update issue: `node skills/linear/scripts/linear-cli.js updateIssue "issueId" '{"stateId":"state-uuid"}'`

### Assign issue to yourself

1. Get your user ID: `node skills/linear/scripts/linear-cli.js user`
2. Update issue: `node skills/linear/scripts/linear-cli.js updateIssue "issueId" '{"assigneeId":"your-user-id"}'`

## Output Format

All commands return JSON. Parse output for programmatic use or display to user as needed.
