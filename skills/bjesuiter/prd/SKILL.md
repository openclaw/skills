---
name: prd
description: Create and manage Product Requirements Documents (PRDs) for AI coding agents. Use when: (1) Creating structured task lists for autonomous coding, (2) Specifying features with user stories and acceptance criteria, (3) Setting up Ralph pattern agentic loops, (4) Planning feature implementation for AI agents.
---

# PRD Skill for AI Agents

Create Product Requirements Documents (PRDs) that power autonomous AI coding agents. Based on the **Ralph Wiggum pattern** by Geoffrey Huntley.

## What is a PRD?

A **PRD (Product Requirements Document)** is a structured specification that:

1. Breaks a feature into **small, independent user stories**
2. Defines **verifiable acceptance criteria** for each story
3. Orders tasks by **dependency** (schema → backend → UI)
4. Enables **autonomous execution** without human intervention

```bash
while :; do cat PROMPT.md | claude-code ; done
```

## Quick Start

1. Create markdown PRD in `tasks/prd-[feature-name].md`
2. Convert to `prd.json` format
3. Run agentic loop with your preferred AI coding agent

## prd.json Format

```json
{
  "project": "MyApp",
  "branchName": "ralph/feature-name",
  "description": "Short description of the feature",
  "userStories": [
    {
      "id": "US-001",
      "title": "Add priority field to database",
      "description": "As a developer, I need to store task priority so it persists.",
      "acceptanceCriteria": [
        "Add priority column: 'high' | 'medium' | 'low'",
        "Generate and run migration",
        "Typecheck passes"
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

### Field Descriptions

| Field | Description |
|-------|-------------|
| `project` | Project name for context |
| `branchName` | Git branch for this feature (prefix with `ralph/`) |
| `description` | One-line feature summary |
| `userStories` | List of stories to complete |
| `userStories[].id` | Unique identifier (US-001, US-002, etc.) |
| `userStories[].title` | Short descriptive title |
| `userStories[].description` | "As a [user], I want [feature] so that [benefit]" |
| `userStories[].acceptanceCriteria` | Verifiable checklist items |
| `userStories[].priority` | Execution order (1 = first) |
| `userStories[].passes` | Completion status (`false` → `true` when done) |
| `userStories[].notes` | Runtime notes added by agent |

## Story Sizing: The #1 Rule

**Each story must complete in ONE context window.** The agent spawns fresh with no memory.

### ✅ Right-sized:
- Add a database column and migration
- Add a UI component to an existing page
- Update a server action with new logic
- Add a filter dropdown to a list

### ❌ Too large (split these):
- "Build the entire dashboard" → Split into: schema, queries, UI, filters
- "Add authentication" → Split into: schema, middleware, login UI, session
- "Refactor the API" → Split into one story per endpoint

**Rule:** If you can't describe it in 2-3 sentences, it's too big.

## Story Ordering

Stories execute in priority order. Earlier stories must NOT depend on later ones.

**Correct order:**
1. Schema/database changes (migrations)
2. Server actions / backend logic
3. UI components that use the backend
4. Dashboard/summary views

## Acceptance Criteria

Must be verifiable, not vague.

### ✅ Good:
- "Add `status` column to tasks table with default 'pending'"
- "Filter dropdown has options: All, Active, Completed"
- "Typecheck passes"

### ❌ Bad:
- "Works correctly"
- "User can do X easily"
- "Good UX"

**Always include:** `"Typecheck passes"`

## Unattended Agentic Loop

### Claude Code
```bash
while :; do
  claude --print --dangerously-skip-permissions \
    "Read prd.json, find first story where passes=false, implement it, run checks, update passes=true if successful"
done
```

### OpenCode
```bash
opencode run "Load prd.json, implement next incomplete story, verify, mark complete"
```

### Key Files

| File | Purpose |
|------|---------|
| `prd.json` | Task list with completion status |
| `prompt.md` | Instructions for each iteration |
| `progress.txt` | Append-only learnings log |

## Human-in-the-Loop

### Manual Story-by-Story
```bash
claude "Implement US-001 from prd.json"
# Review, approve, continue to US-002
```

### Git Worktree Strategy
```bash
# Create worktree for feature
git worktree add ../myapp-feature ralph/feature-name

# Run agent in worktree
cd ../myapp-feature
claude "Implement prd.json stories"

# Review in main repo
cd ../myapp && git diff main..ralph/feature-name
```

## Agent Prompt Template

```markdown
# Agent Instructions

1. Read `prd.json`
2. Read `progress.txt` (check Codebase Patterns first)
3. Checkout/create branch from PRD `branchName`
4. Pick highest priority story where `passes: false`
5. Implement that single story
6. Run quality checks (typecheck, lint, test)
7. If checks pass, commit: `feat: [Story ID] - [Story Title]`
8. Update prd.json: set `passes: true`
9. Append progress to `progress.txt`

**Stop Condition:** When ALL stories have `passes: true`, output:
<promise>COMPLETE</promise>
```

## Progress Tracking

Append to `progress.txt` after each iteration (never replace):

```markdown
## 2026-01-10 18:00 - US-001
- Implemented: Added priority column to tasks table
- Files changed: migrations/001_add_priority.sql, src/types.ts
- **Learnings:** Use `IF NOT EXISTS` for migrations
---
```

### Codebase Patterns (at top of progress.txt)

```markdown
## Codebase Patterns
- Use `sql<number>` template for aggregations
- Always use `IF NOT EXISTS` for migrations
- Export types from actions.ts for UI components
```

## Quick Reference

| Action | Command |
|--------|---------|
| Create PRD | Save markdown to `tasks/prd-[name].md` |
| Convert to JSON | `claude "Convert tasks/prd-x.md to prd.json"` |
| Run autonomous | `while :; do cat prompt.md \| claude; done` |
| Check status | `cat prd.json \| jq '.userStories[] \| {id, passes}'` |

## Checklist Before Running

- [ ] Each story completable in one context window
- [ ] Stories ordered by dependency (schema → backend → UI)
- [ ] Every story has "Typecheck passes" criterion
- [ ] Acceptance criteria are verifiable (not vague)
- [ ] No story depends on a later story

## Resources

See `references/` for detailed documentation:
- `workflows.md` - Sequential workflow patterns
- `output-patterns.md` - Template and example patterns
