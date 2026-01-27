# GitNotesMemory

**Git-Based Knowledge Graph Memory System for Claude Code**

A persistent, branch-aware memory system that uses git notes to store and retrieve contextual information across sessions. Designed as a Claude Code skill for automatic, silent operation.

## Features

- **Git-Native Storage** - Uses `git notes` for persistence (survives branches, stays local, never pushed)
- **Branch-Aware** - Each branch has its own memory context with automatic inheritance
- **Knowledge Graph** - Entity extraction and linking for intelligent retrieval
- **Token-Efficient** - Tiered retrieval system minimizes context usage
- **Domain-Agnostic** - Works with any content type (code, docs, research, learning)
- **Silent Operation** - Runs automatically without user prompts

## How It Works

### Storage Architecture

```
.git/
└── refs/notes/
    ├── mem-main        # Memory data for main branch
    ├── mem-feature     # Memory data for feature branch
    ├── ent-main        # Entity index for main branch
    ├── ent-feature     # Entity index for feature branch
    ├── idx-main        # Compact index for main branch
    └── idx-feature     # Compact index for feature branch
```

Notes are attached to the repository's root commit, ensuring they persist across all operations while remaining branch-specific.

### Tiered Retrieval

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 0: sync --start                          ~50 tokens   │
│ Returns: branch, topics, critical memories, counts         │
├─────────────────────────────────────────────────────────────┤
│ TIER 1: get <topic>                          ~100 tokens   │
│ Returns: memories related to a specific topic              │
├─────────────────────────────────────────────────────────────┤
│ TIER 2: recall -i <id>                       Full data     │
│ Returns: complete memory entry (on-demand only)            │
└─────────────────────────────────────────────────────────────┘
```

### Branch Workflow

```
main ─────●─────●─────●─────●─────●───────●─────►
          │                 ▲             │
          │   feature       │   merge     │
          └────●────●───────┘   memories  │
               │    │                     │
          memories  memories         merge-branch
          inherited created          feature
```

1. **Create branch** → Automatically inherits memories from main/master
2. **Work on branch** → New memories stored in branch-specific notes
3. **Merge branch** → Run `merge-branch` to combine memories

## Installation

### As a Claude Code Skill

1. Copy the `git-notes-memory` folder to your skills directory:
   ```bash
   cp -r git-notes-memory ~/.claude/skills/
   ```

2. Or symlink for development:
   ```bash
   ln -s /path/to/git-notes-memory ~/.claude/skills/git-notes-memory
   ```

### Enable in Your Project

Add a `CLAUDE.md` file to your project root to activate the skill:

```markdown
# Memory

YOU MUST ALWAYS USE `git-notes-memory` SKILL.
```

This instructs Claude to automatically use the memory skill for the project.

### Standalone Usage

```bash
python3 memory.py -p /path/to/project <command>
```

## Commands

### Session Management

| Command | Description |
|---------|-------------|
| `sync --start` | Initialize session, return compact context |
| `sync --end '{"summary": "..."}'` | End session, store summary |

### Memory Operations

| Command | Description |
|---------|-------------|
| `remember '{"key": "value"}' -i h` | Store memory with importance |
| `recall` | Overview of all memories |
| `recall -i <id>` | Get full memory by ID |
| `recall --last 5` | Get last 5 memories |
| `get <topic>` | Get memories related to topic |
| `update <id> '{}' -m` | Update memory (merge mode) |
| `evolve <id> "note"` | Add evolution note |
| `forget <id>` | Delete memory |

### Entity Operations

| Command | Description |
|---------|-------------|
| `entities` | List all entities with counts |
| `entity <name>` | Get entity details and linked memories |

### Branch Operations

| Command | Description |
|---------|-------------|
| `branches` | List branches with memory counts |
| `merge-branch <source>` | Merge memories from another branch |

### Importance Levels

| Flag | Level | Use Case |
|------|-------|----------|
| `-i c` | Critical | Must never forget (user preferences, key decisions) |
| `-i h` | High | Important (architecture, major decisions) |
| `-i n` | Normal | Standard (default) |
| `-i l` | Low | Temporary (can be pruned) |

## Memory Types

Memories are automatically classified based on content:

| Type | Trigger Words |
|------|---------------|
| `decision` | decided, chose, picked, selected, opted |
| `preference` | prefer, favorite, like best, rather |
| `learning` | learned, studied, understood, realized |
| `task` | todo, need to, plan to, next step |
| `question` | wondering, curious, research, investigate |
| `note` | noticed, observed, important |
| `progress` | completed, finished, achieved |
| `info` | (default) |

## Entity Extraction

Entities are automatically extracted from content:

- **Explicit fields**: `topic`, `subject`, `name`, `category`
- **Hashtags**: `#cooking`, `#project`, `#important`
- **Quoted phrases**: `"French Revolution"`, `"quick sort"`
- **Capitalized words**: `Paris`, `Einstein`, `Monday`
- **Key terms**: Meaningful words (stop words filtered)

## Output Format

### Tier 0: Session Start
```json
{
  "b": "main",
  "t": {"auth": 5, "database": 3, "api": 2},
  "c": [{"id": "abc123", "s": "prefer TypeScript", "t": "preference"}],
  "n": 42,
  "h": [{"id": "def456", "s": "use PostgreSQL"}]
}
```

### Tier 1: Topic Query
```json
{
  "topic": "auth",
  "mem": [
    {"id": "abc123", "s": "decided OAuth2", "t": "decision", "i": "h", "b": "main"},
    {"id": "def456", "s": "JWT for sessions", "t": "decision", "i": "n", "b": "feature"}
  ]
}
```

### Tier 2: Full Memory
```json
{
  "d": {"decision": "Use OAuth2", "reason": "Better security"},
  "e": ["auth", "oauth2", "security"],
  "t": "decision",
  "g": ["architecture"],
  "i": "h",
  "b": "main",
  "c": "2024-01-15T10:30:00",
  "u": "2024-01-15T10:30:00",
  "a": 3
}
```

## Example Usage

### Basic Session
```bash
# Start session
python3 memory.py -p . sync --start

# Remember something
python3 memory.py -p . remember '{"decision": "use React", "reason": "team expertise"}' -i h

# Query topic
python3 memory.py -p . get frontend

# End session
python3 memory.py -p . sync --end '{"summary": "Set up frontend architecture"}'
```

### Branch Workflow
```bash
# On main branch
python3 memory.py -p . remember '{"project": "webapp", "stack": "React + Node"}'

# Switch to feature branch
git checkout -b feature/auth

# Start session (auto-inherits from main)
python3 memory.py -p . sync --start

# Add branch-specific memories
python3 memory.py -p . remember '{"auth": "OAuth2", "provider": "Auth0"}' -i h

# After merging in git
git checkout main
git merge feature/auth

# Merge memories
python3 memory.py -p . merge-branch feature-auth
```

## Skill Integration

When used as a Claude Code skill, the system operates **silently**:

1. **Never asks** "should I remember this?"
2. **Never announces** "I'll remember that"
3. **Never shows** command output to users
4. **Automatically** manages memory lifecycle

### Session Protocol

```
Session Start:
  → sync --start
  → Use context to inform responses

During Session:
  → Silently remember decisions, preferences, learnings
  → Query topics when relevant context needed

Session End:
  → sync --end with session summary
```

## Technical Details

### Data Model

**Memory Entry:**
```python
{
    "d": Any,           # Data (the actual content)
    "e": List[str],     # Entities (auto-extracted)
    "t": str,           # Type (decision, preference, etc.)
    "g": List[str],     # Tags
    "i": str,           # Importance (c/h/n/l)
    "b": str,           # Branch (originating branch)
    "c": str,           # Created (ISO timestamp)
    "u": str,           # Updated (ISO timestamp)
    "a": int            # Access count
}
```

**Index Entry (compact):**
```python
{
    "s": str,           # Summary (50 chars max)
    "e": List[str],     # Top 3 entities
    "t": str,           # Type
    "i": str,           # Importance
    "u": str            # Updated (date only)
}
```

### Merge Strategy

When merging memories from another branch:

- **New keys**: Added directly
- **Nested dicts**: Recursively merged
- **Lists**: Union (no duplicates)
- **Conflicting memories**: Keep latest by update time
- **Topic counts**: Take maximum

## Requirements

- Python 3.7+
- Git (any recent version)
- No external dependencies

## License

MIT

## Contributing

Contributions welcome! Please ensure any changes maintain:
- Silent operation (no user prompts)
- Token efficiency (compact outputs)
- Branch awareness (proper isolation)
- Domain agnosticism (no tech-specific patterns)
