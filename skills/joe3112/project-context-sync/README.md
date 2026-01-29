# project-context-sync

Keep a living `PROJECT_STATE.md` updated after each commit, so any agent (or future session) can instantly understand where things stand.

## How It Works

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
# Clone this repo (or download it)
git clone https://github.com/Joe3112/project-context-sync.git

# From the repo you want to enable:
cd /path/to/your/project
/path/to/project-context-sync/scripts/install.sh
```

This will:
- Install a post-commit hook in `.git/hooks/`
- Create `.project-context.yml` with default config
- Create initial `PROJECT_STATE.md`
- Add `PROJECT_STATE.md` to `.gitignore`

## Uninstall

```bash
cd /path/to/your/project
/path/to/project-context-sync/scripts/uninstall.sh
```

## Manual Update

Trigger an update without committing:

```bash
/path/to/project-context-sync/scripts/update-context.sh
```

## Configuration

Edit `.project-context.yml` in your repo root:

```yaml
project_context:
  # Use AI to generate smart summaries (requires Clawdbot)
  ai_summary: true
  
  # How many recent commits to include
  recent_commits: 5
  
  # Include diff stats in context
  include_diff_stats: true
```

### AI Mode vs Raw Mode

| Mode | `ai_summary` | What You Get |
|------|--------------|--------------|
| **AI** | `true` | Intelligent summaries, inferred focus, suggested next steps |
| **Raw** | `false` | Just git info — fast, free, no dependencies |

## AI Mode Setup (Clawdbot)

AI summaries require [Clawdbot](https://github.com/clawdbot/clawdbot) with the HTTP API enabled:

```json
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

The script reads your gateway config from `~/.clawdbot/clawdbot.json` automatically.

**Security:** The endpoint uses bearer token auth and binds to localhost by default — only local processes can access it.

## Example Output

```markdown
# Project State
*Auto-updated: 2026-01-29 12:34:01*

## Last Commit
- **Hash:** 3c95bad
- **Message:** fix: use OpenAI-compatible endpoint for AI summaries
- **Author:** Joe3112
- **Date:** 2026-01-29 12:34:01 +0100
- **Changes:** 2 files changed, 29 insertions(+), 4 deletions(-)

## Recent Changes
- `3c95bad` fix: use OpenAI-compatible endpoint for AI summaries
- `bd2a8c3` feat: AI mode reads gateway config
- `ddb0024` fix: improve raw mode messaging

## Current Focus
Developing the project-context-sync skill with AI-powered summaries...

## Suggested Next Steps
- Test AI summary generation end-to-end
- Add error handling when AI endpoint is unavailable
- Document configuration options
```

## License

MIT
