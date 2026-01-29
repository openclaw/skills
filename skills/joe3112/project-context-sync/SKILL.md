# project-context-sync

Keep a living project state document updated after each commit, so any agent (or future session) can instantly understand where things stand.

## What It Does

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│ Git Commit  │ ──▶ │ Post-commit Hook │ ──▶ │ PROJECT_STATE.md    │
│             │     │                  │     │ (auto-updated)      │
└─────────────┘     └──────────────────┘     └─────────────────────┘
```

After each commit, the hook:
1. Gathers git info (last commit, recent history, branch, changed files)
2. Optionally calls an LLM to generate a smart summary
3. Updates `PROJECT_STATE.md` in the repo root

## Installation

```bash
# From the repo you want to enable:
cd /path/to/your/repo
/path/to/skills/project-context-sync/scripts/install.sh
```

Or if you have the skill in your path:
```bash
project-context-sync install
```

This will:
1. Install a post-commit hook in `.git/hooks/`
2. Create `.project-context.yml` with default config
3. Create initial `PROJECT_STATE.md`
4. Add `PROJECT_STATE.md` to `.gitignore`

## Uninstall

```bash
cd /path/to/your/repo
/path/to/skills/project-context-sync/scripts/uninstall.sh
```

## Manual Update

Trigger an update without committing:

```bash
cd /path/to/your/repo
/path/to/skills/project-context-sync/scripts/update-context.sh
```

## Configuration

Edit `.project-context.yml` in your repo root:

```yaml
project_context:
  # Use AI to generate smart summaries (default: true)
  ai_summary: true
  
  # How many recent commits to include
  recent_commits: 5
  
  # Include diff stats in context
  include_diff_stats: true
  
  # Sections to include
  sections:
    - last_commit
    - recent_changes
    - current_focus    # AI-generated
    - suggested_next   # AI-generated
```

### AI Summary Mode

**With `ai_summary: true`** (default):
- Generates intelligent summaries of what changed
- Infers current focus from recent commit patterns
- Suggests next steps
- Costs tokens but provides rich context
- **Requires:** Gateway HTTP API enabled (see below)

**With `ai_summary: false`**:
- Just logs raw git info
- Fast and free
- Less intelligent but still useful

### Enabling the Gateway HTTP API

AI mode uses Clawdbot's OpenAI-compatible endpoint (`/v1/chat/completions`). This is **disabled by default** for security. To enable:

```json5
// ~/.clawdbot/clawdbot.json
{
  "gateway": {
    "http": {
      "endpoints": {
        "chatCompletions": { "enabled": true }
      }
    }
  }
}
```

**Security notes:**
- The endpoint inherits gateway auth (requires bearer token)
- With `bind: "loopback"` (default), only local processes can connect
- The script reads the token from `~/.clawdbot/clawdbot.json` automatically
- Risk is minimal for local development setups

## Output

`PROJECT_STATE.md` will contain:

```markdown
# Project State
*Auto-updated by project-context-sync*

## Last Commit
- **Hash:** abc123
- **Message:** Implement isPro check for app blocking
- **Branch:** feature/subscription-gating
- **When:** 2026-01-29 12:34
- **Files changed:** 3

## Recent Changes
- abc123: Implement isPro check for app blocking
- def456: Add PaywallPrompt component
- ...

## Current Focus
[AI-generated summary of what's being worked on]

## Suggested Next Steps
[AI-suggested based on commit patterns]
```

## Notes

- `PROJECT_STATE.md` is gitignored by default (regenerated locally)
- The hook requires Clawdbot to be running for AI summaries
- Without Clawdbot, falls back to raw git info mode
