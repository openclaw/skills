---
name: idea-exploration
description: Launch background Claude sessions to explore and analyze business ideas. Say "Idea: [description]" to trigger.
homepage: https://github.com/anthropics/claude-code
metadata: {"clawdbot":{"emoji":"💡","requires":{"bins":["claude","tmux","telegram"]}}}
---

# Idea Exploration Skill

Launch autonomous Claude Code sessions to explore business ideas in depth. Get market research, technical analysis, GTM strategy, and actionable recommendations.

## Quick Start

**Trigger phrase:** Say `Idea: [description]` and the assistant will:
1. Spin up a Claude Code session in tmux
2. Research and analyze the idea comprehensively
3. Save results to `~/clawd/ideas/<slug>/research.md`
4. Send file to your Telegram Saved Messages
5. Notify you via cron when complete

## How It Works

```
User: "Idea: AI calendar assistant"
       ↓
┌─────────────────────────────────┐
│  1. explore-idea.sh starts      │
│  2. Creates tmux session        │
│  3. Runs Claude Code            │
│  4. Claude analyzes & writes    │
│  5. notify-research-complete.sh │
│     → Sends file to "me"        │
│     → Queues notification       │
│  6. Cron checks queue (1 min)   │
│  7. Notifies user in chat       │
└─────────────────────────────────┘
```

## Setup

### Prerequisites
- `claude` CLI (Claude Code)
- `tmux`
- `telegram` CLI (supertelegram)
- Clawdbot with cron enabled

### 1. Create Scripts

See `~/clawd/scripts/explore-idea.sh` for the full implementation.

Key components:
- Creates idea directory with prompt and runner script
- Unsets OAuth env vars to use Claude Max
- Runs claude with `--dangerously-skip-permissions`
- Calls notify script on completion

### 2. Set Up Cron Job

```bash
# Cron job to check notification queue every minute
{
  name: "Check notification queue",
  sessionTarget: "isolated",
  wakeMode: "now",
  payload: {
    kind: "agentTurn",
    message: "Check ~/.clawdbot/notify-queue/ for .json files...",
    deliver: true,
    channel: "telegram",
    to: "YOUR_CHAT_ID"
  },
  schedule: { kind: "every", everyMs: 60000 }
}
```

### 3. Add AGENTS.md Instructions

```markdown
**When user says "Idea: [description]":**
1. Extract the idea description
2. Execute: `CLAWD_SESSION_KEY="main" ~/clawd/scripts/explore-idea.sh "[idea]"`
3. Confirm: "Idea exploration started. You'll be notified when complete."
```

## Analysis Framework

The exploration covers:

1. **Core Concept Analysis** - Problem, assumptions, uniqueness
2. **Market Research** - Users, TAM/SAM/SOM, competitors
3. **Technical Implementation** - Stack, MVP scope, challenges
4. **Business Model** - Revenue, pricing, unit economics
5. **Go-to-Market Strategy** - Launch, acquisition, partnerships
6. **Risks & Challenges** - Technical, competitive, regulatory
7. **Verdict & Recommendations** - Clear yes/no with action plan

## Verdict Types

- 🟢 **STRONG YES** - Clear opportunity, pursue aggressively
- 🟡 **CONDITIONAL YES** - Promising but needs validation
- 🟠 **PIVOT RECOMMENDED** - Core insight good, execution needs work
- 🔴 **PASS** - Too many red flags

## Example Output

```
~/clawd/ideas/ai-calendar-assistant/
├── metadata.txt
├── prompt.txt
├── run-claude.sh
└── research.md    # 400-500 line comprehensive analysis
```

## Tips

- Ideas typically take 3-5 minutes to analyze
- Monitor progress: `tmux attach -t idea-<slug>-<timestamp>`
- File goes to Saved Messages even if notification fails
- Check `~/.clawdbot/notify-queue/` for stuck notifications
