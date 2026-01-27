---
name: git-notes-memory
description: Git-Notes-Based knowledge graph memory system. Claude should use this SILENTLY and AUTOMATICALLY - never ask users about memory operations. Branch-aware persistent memory using git notes. Handles context, decisions, tasks, and learnings across sessions.
---

# GitNotesMemory - Claude Integration Guide

## CRITICAL: SILENT OPERATION RULES

**These rules are ABSOLUTE and must NEVER be violated:**

1. **NEVER ask** "should I remember?" or "want me to save?"
2. **NEVER announce** "I'll remember this" or "saving to memory"
3. **NEVER show** memory command output to users
4. **NEVER mention** memory system unless user explicitly asks about it
5. **JUST DO IT** - silently in the background

## Quick Reference

```bash
# Replace $SKILL_PATH with actual path to memory.py
# Replace $DIR with the project directory path

python3 $SKILL_PATH/memory.py -p $DIR <command>
```

### Essential Commands

| Command | When to Use |
|---------|-------------|
| `sync --start` | **ALWAYS** at session start |
| `sync --end '{"summary":"..."}'` | At session end (optional but recommended) |
| `remember '{"..."}' -t tags -i h` | Store important information |
| `get <topic>` | Retrieve context about a topic |
| `search "<query>"` | Full-text search across all memories |
| `recall -i <id>` | Get full details of a specific memory |

### Importance Flags

| Flag | Level | When to Use |
|------|-------|-------------|
| `-i c` | Critical | User says "always remember", "never forget", explicit preferences |
| `-i h` | High | Decisions, architecture choices, user corrections, preferences |
| `-i n` | Normal | General information (default) |
| `-i l` | Low | Temporary notes, might be pruned |

## Session Lifecycle

### 1. Session Start (MANDATORY)

**Always run `sync --start` at the beginning of every session:**

```bash
python3 $SKILL_PATH/memory.py -p $DIR sync --start
```

**Output explains:**
```json
{
  "b": "main",           // Current git branch
  "t": {"api": 5, "auth": 3},  // Top topics with memory counts
  "c": [...],            // Critical memories (always review these)
  "n": 42,               // Total memory count
  "h": [...]             // High-importance recent memories
}
```

**Use this context to:**
- Understand what the user has been working on
- Reference previous decisions
- Maintain continuity across sessions

### 2. During Session

**Silently remember when user:**
- Makes a decision: "Let's use PostgreSQL" → remember with `-i h`
- States a preference: "I prefer tabs over spaces" → remember with `-i h` or `-i c`
- Learns something: "Oh, so that's how async works" → remember with `-i n`
- Sets a task: "We need to fix the login bug" → remember with `-i n`
- Shares important context: Project requirements, constraints, goals

**Retrieve context when:**
- User asks about something previously discussed → `get <topic>`
- You need to recall a specific decision → `search "<keywords>"`
- User references "what we decided" → check relevant memories

### 3. Session End (Recommended)

```bash
python3 $SKILL_PATH/memory.py -p $DIR sync --end '{"summary": "Brief session summary"}'
```

## Memory Content Best Practices

### Good Memory Structure

**For decisions:**
```json
{"decision": "Use React for frontend", "reason": "Team expertise", "alternatives": ["Vue", "Angular"]}
```

**For preferences:**
```json
{"preference": "Detailed explanations", "context": "User prefers thorough explanations over brief answers"}
```

**For learnings:**
```json
{"topic": "Authentication", "learned": "OAuth2 flow requires redirect URI configuration"}
```

**For tasks:**
```json
{"task": "Implement user dashboard", "status": "in progress", "blockers": ["API not ready"]}
```

**For notes:**
```json
{"subject": "Project Architecture", "note": "Microservices pattern with API gateway"}
```

### Tags

Use tags to categorize memories for better retrieval:
- `-t architecture,backend` - Technical categories
- `-t urgent,bug` - Priority/type markers
- `-t meeting,requirements` - Source context

## Command Reference

### Core Commands

#### `sync --start`
Initialize session, get context overview.
```bash
python3 $SKILL_PATH/memory.py -p $DIR sync --start
```

#### `sync --end`
End session with summary (triggers maintenance).
```bash
python3 $SKILL_PATH/memory.py -p $DIR sync --end '{"summary": "Implemented auth flow"}'
```

#### `remember`
Store a new memory.
```bash
python3 $SKILL_PATH/memory.py -p $DIR remember '{"key": "value"}' -t tag1,tag2 -i h
```

#### `get`
Get memories related to a topic (searches entities, tags, and content).
```bash
python3 $SKILL_PATH/memory.py -p $DIR get authentication
```

#### `search`
Full-text search across all memories.
```bash
python3 $SKILL_PATH/memory.py -p $DIR search "database migration"
```

#### `recall`
Retrieve memories by various criteria.
```bash
# Get full memory by ID
python3 $SKILL_PATH/memory.py -p $DIR recall -i abc123

# Get memories by tag
python3 $SKILL_PATH/memory.py -p $DIR recall -t architecture

# Get last N memories
python3 $SKILL_PATH/memory.py -p $DIR recall --last 5

# Overview of all memories
python3 $SKILL_PATH/memory.py -p $DIR recall
```

### Update Commands

#### `update`
Modify an existing memory.
```bash
# Replace content
python3 $SKILL_PATH/memory.py -p $DIR update <id> '{"new": "content"}'

# Merge content (add to existing)
python3 $SKILL_PATH/memory.py -p $DIR update <id> '{"extra": "field"}' -m

# Change importance
python3 $SKILL_PATH/memory.py -p $DIR update <id> -i c

# Update tags
python3 $SKILL_PATH/memory.py -p $DIR update <id> -t newtag1,newtag2
```

#### `evolve`
Add an evolution note to track changes over time.
```bash
python3 $SKILL_PATH/memory.py -p $DIR evolve <id> "User changed preference to dark mode"
```

#### `forget`
Delete a memory (use sparingly).
```bash
python3 $SKILL_PATH/memory.py -p $DIR forget <id>
```

### Entity Commands

#### `entities`
List all extracted entities with counts.
```bash
python3 $SKILL_PATH/memory.py -p $DIR entities
```

#### `entity`
Get details about a specific entity.
```bash
python3 $SKILL_PATH/memory.py -p $DIR entity authentication
```

### Branch Commands

#### `branches`
List all branches with memory counts.
```bash
python3 $SKILL_PATH/memory.py -p $DIR branches
```

#### `merge-branch`
Merge memories from another branch (run after git merge).
```bash
python3 $SKILL_PATH/memory.py -p $DIR merge-branch feature-auth
```

## Branch Awareness

### How It Works

- Each git branch has **isolated memory storage**
- New branches **automatically inherit** from main/master
- After git merge, run `merge-branch` to combine memories

### Branch Workflow

```
1. User on main branch → memories stored in refs/notes/mem-main
2. User creates feature branch → auto-inherits main's memories
3. User works on feature → new memories stored in refs/notes/mem-feature-xxx
4. After git merge → run merge-branch to combine memories
```

## Memory Types (Auto-Detected)

The system automatically classifies memories based on content:

| Type | Trigger Words |
|------|---------------|
| `decision` | decided, chose, picked, selected, opted, going with |
| `preference` | prefer, favorite, like best, rather, better to |
| `learning` | learned, studied, understood, realized, discovered |
| `task` | todo, task, need to, plan to, next step, going to |
| `question` | wondering, curious, research, investigate, find out |
| `note` | noticed, observed, important, remember that |
| `progress` | completed, finished, done, achieved, milestone |
| `info` | (default for unclassified content) |

## Entity Extraction

Entities are automatically extracted for intelligent retrieval:

- **Explicit fields**: `topic`, `subject`, `name`, `category`, `area`, `project`
- **Hashtags**: `#cooking`, `#urgent`, `#v2`
- **Quoted phrases**: `"machine learning"`, `"user authentication"`
- **Capitalized words**: `React`, `PostgreSQL`, `Monday`
- **Key terms**: Meaningful words (common words filtered out)

## What to Remember

**DO remember:**
- User decisions and their rationale
- Stated preferences (coding style, communication style, tools)
- Project architecture and constraints
- Important context that affects future work
- Tasks, blockers, and progress
- Corrections ("actually, I meant..." → high importance)
- Explicit requests to remember something → critical importance

**DON'T remember:**
- Trivial conversation
- Information easily derivable from code
- Secrets, passwords, API keys
- One-time questions with no future relevance
- Duplicate information already stored

## Output Format Reference

### Tier 0: sync --start
```json
{
  "b": "feature-auth",                    // Current branch
  "t": {"auth": 5, "api": 3, "db": 2},   // Topics with counts
  "c": [{"id": "x", "s": "summary", "t": "preference"}],  // Critical
  "n": 15,                                // Total count
  "h": [{"id": "y", "s": "summary"}]     // High importance
}
```

### Tier 1: get/search
```json
{
  "topic": "auth",
  "mem": [
    {"id": "abc", "s": "decided OAuth2", "t": "decision", "i": "h", "b": "main"}
  ]
}
```

### Tier 2: recall -i <id>
```json
{
  "d": {"decision": "Use OAuth2"},  // Full data
  "e": ["auth", "oauth2"],          // Entities
  "t": "decision",                   // Type
  "g": ["architecture"],             // Tags
  "i": "h",                          // Importance
  "b": "main",                       // Branch
  "c": "2024-01-15T10:30:00",       // Created
  "u": "2024-01-15T10:30:00",       // Updated
  "a": 3,                            // Access count
  "ev": [{"n": "note", "t": "..."}] // Evolution notes (if any)
}
```

## Example Silent Flow

```
User: "Let's build a REST API with Python"
Claude: [silently: remember '{"decision": "REST API", "language": "Python"}' -t architecture -i h]
        [responds about REST API setup WITHOUT mentioning memory]

User: "I prefer FastAPI over Flask"
Claude: [silently: remember '{"preference": "FastAPI over Flask", "reason": "user preference"}' -i h]
        [continues discussion using FastAPI WITHOUT saying "I'll remember"]

User: "What did we decide about the API?"
Claude: [silently: get api]
        [uses retrieved context to answer accurately]

User: "Actually, let's use Flask instead"
Claude: [silently: remember '{"decision": "Changed to Flask", "previous": "FastAPI"}' -i h]
        [silently: evolve <fastapi-memory-id> "User changed preference to Flask"]
        [acknowledges change WITHOUT mentioning memory update]
```

## Troubleshooting

**Memory not found:**
- Use `search` with different keywords
- Check `entities` to see what's indexed
- Use `recall --last 10` to see recent memories

**Context seems stale:**
- Always run `sync --start` at session beginning
- Check current branch with `branches`

**After git operations:**
- After `git merge`: run `merge-branch <source-branch>`
- After `git checkout`: `sync --start` will load correct branch context
