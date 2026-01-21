---
name: agent-registry
description: |
  MANDATORY agent discovery system for token-efficient agent loading. Claude MUST use this skill 
  instead of loading agents directly from ~/.claude/agents/ or .claude/agents/. Provides lazy 
  loading via search_agents and get_agent tools. Use when: (1) user task may benefit from 
  specialized agent expertise, (2) user asks about available agents, (3) starting complex 
  workflows that historically used agents. This skill reduces context window usage by ~95% 
  compared to loading all agents upfront.
---

# Agent Registry

Lazy-loading system for Claude Code agents. Eliminates the "~16k tokens" warning by loading agents on-demand.

## CRITICAL RULE

**NEVER assume agents are pre-loaded.** Always use this registry to discover and load agents.

## Workflow

```
User Request → search_agents(intent) → select best match → get_agent(name) → execute with agent
```

## Available Commands

| Command | When to Use | Example |
|---------|-------------|---------|
| `list_agents.py` | User asks "what agents do I have" or needs overview | `python scripts/list_agents.py` |
| `search_agents.py` | Find agents matching user intent (ALWAYS do this first) | `python scripts/search_agents.py "code review security"` |
| `search_agents_paged.py` | Paged search for large registries (300+ agents) | `python scripts/search_agents_paged.py "query" --page 1 --page-size 10` |
| `get_agent.py` | Load a specific agent's full instructions | `python scripts/get_agent.py code-reviewer` |

## Search First Pattern

1. **Extract intent keywords** from user request
2. **Run search**: `python scripts/search_agents.py "<keywords>"`
3. **Review results**: Check relevance scores (0.0-1.0)
4. **Load if needed**: `python scripts/get_agent.py <agent-name>`
5. **Execute**: Follow the loaded agent's instructions

## Example

User: "Can you review my authentication code for security issues?"

```bash
# Step 1: Search for relevant agents
python scripts/search_agents.py "code review security authentication"

# Output:
# Found 2 matching agents:
#   1. security-auditor (score: 0.89) - Analyzes code for security vulnerabilities
#   2. code-reviewer (score: 0.71) - General code review and best practices

# Step 2: Load the best match
python scripts/get_agent.py security-auditor

# Step 3: Follow loaded agent instructions for the task
```

## Installation

### Step 1: Install the Skill

**Quick Install (Recommended):**

```bash
# NPX with add-skill (recommended)
npx add-skill MaTriXy/Agent-Registry

# OR npm directly
npm install -g @claude-code/agent-registry
```

**Traditional Install:**

```bash
# User-level installation
./install.sh

# OR project-level installation
./install.sh --project
```

**What install.sh does:**
1. ✓ Copies skill files to `~/.claude/skills/agent-registry/`
2. ✓ Creates empty registry structure
3. ✓ Automatically installs `questionary` Python package (for interactive UI)
4. ✓ Falls back gracefully if `pip3` not available

**Note:** All installation methods support Python-based migration and CLI tools

### Step 2: Migrate Your Agents

Run the interactive migration script:

```bash
cd ~/.claude/skills/agent-registry
python scripts/init_registry.py
```

**Interactive selection modes:**

- **With questionary** (recommended): Checkbox UI with category grouping, token indicators, and paging
  - ↑↓ navigate, Space toggle, Enter confirm
  - Visual indicators: 🟢 <1k tokens, 🟡 1-3k, 🔴 >3k
  - Grouped by subdirectory

- **Without questionary** (fallback): Text-based number input
  - Enter comma-separated numbers (e.g., `1,3,5`)
  - Type `all` to migrate everything

**What init_registry.py does:**
1. Scans `~/.claude/agents/` and `.claude/agents/` for agent files
2. Displays available agents with metadata
3. Lets you interactively select which to migrate
4. Moves selected agents to the registry
5. Builds search index (`registry.json`)

## Dependencies

- **Python**: 3.7 or higher
- **questionary**: Interactive checkbox selection UI with Separator support

The installer automatically installs questionary. If installation fails or pip3 is unavailable, the migration script falls back to text-based input mode.

**Manual installation:**
```bash
pip3 install questionary
```

## Registry Location

- **Global**: `~/.claude/skills/agent-registry/`
- **Project**: `.claude/skills/agent-registry/` (optional override)

Agents not migrated remain in their original locations and load normally (contributing to token overhead).
