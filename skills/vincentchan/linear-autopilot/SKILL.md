---
name: linear-autopilot
description: Automate Linear task processing with Discord notifications and git sync. Use when setting up a kanban-to-agent workflow where Linear tasks trigger Clawdbot actions via Discord. Handles task intake, status updates, DM notifications, and auto-push to git. Supports any task type - research, content creation, code tasks, or custom workflows.
---

# Linear Autopilot

Automated pipeline: **Linear → Webhook Service → Discord → Clawdbot → Git**

Tasks created in Linear automatically trigger Clawdbot processing with real-time notifications and git sync for Obsidian/local access.

## Free Tier Limitations

Before setup, be aware of free plan limits:

| Service | Free Tier Limits | Recommendation |
|---------|------------------|----------------|
| **Linear** | 250 issues, unlimited members | Sufficient for most personal/small team use |
| **Pipedream** | 100 invocations/day, 10 workflows | Good for light usage (~3 tasks/day) |
| **Zapier** | 100 tasks/month, 5 zaps, 15-min polling, **no webhooks** | ⚠️ Paid plan required for this workflow |

**Important notes:**
- **Pipedream** free tier resets daily and includes instant webhooks — best free option
- **Zapier** free plan does NOT support webhooks (required for real-time Linear triggers). You need a paid Zapier plan (Starter+) for this workflow to work properly
- For budget-conscious users: **use Pipedream**

## Setup

### 1. Configure Linear API

Run setup to store your Linear API key:

```bash
mkdir -p ~/.clawdbot
echo "LINEAR_API_KEY=lin_api_xxxxx" > ~/.clawdbot/linear.env
```

Get your API key from: Linear → Settings → API → Personal API keys

### 2. Get Linear IDs

Find your team and state IDs:

```bash
./scripts/linear-api.sh teams    # Get team ID
./scripts/linear-api.sh states   # Get state IDs (Todo, In Progress, Done)
```

Update `~/.clawdbot/linear-config.json`:

```json
{
  "teamId": "your-team-id",
  "states": {
    "todo": "state-id-for-todo",
    "inProgress": "state-id-for-in-progress",
    "done": "state-id-for-done"
  },
  "discord": {
    "notifyUserId": "your-discord-user-id",
    "taskChannelId": "your-linear-tasks-channel-id"
  },
  "git": {
    "autoPush": true,
    "commitPrefix": "task:"
  }
}
```

### 3. Set Up Webhook Service

Choose your preferred automation platform:

#### Option A: Pipedream (Recommended for free tier)
- 100 invocations/day free
- Instant webhook triggers
- See `references/pipedream-setup.md` for step-by-step guide

Quick setup:
1. Create workflow at pipedream.com with HTTP webhook trigger
2. Add Linear webhook pointing to your Pipedream URL
3. Add Discord "Send Message" step with Clawdbot bot token
4. Message template:
   ```
   <@BOT_ID>
   📋 New task: {{steps.trigger.event.data.title}}
     Status: {{steps.trigger.event.data.state.name}}
     ID: {{steps.trigger.event.data.identifier}}
   ```

#### Option B: Zapier (If you have a paid account)
- 100 tasks/month on free (very limited)
- Native Linear + Discord integrations
- See `references/zapier-setup.md` for step-by-step guide

Quick setup:
1. Create Zap: Linear (New Issue) → Discord (Send Channel Message)
2. Use webhook or bot integration for Discord
3. Map Linear fields to message template

### 4. Configure Discord Channel

Ensure Clawdbot listens to your task channel. In `clawdbot.json`:

```json
{
  "channels": {
    "discord": {
      "guilds": {
        "YOUR_GUILD_ID": {
          "channels": {
            "YOUR_TASK_CHANNEL_ID": {
              "allow": true,
              "requireMention": false
            }
          }
        }
      }
    }
  }
}
```

## Task Processing Workflow

When a task arrives in the Discord channel:

### 1. Acknowledge
- Reply in channel confirming receipt

### 2. Notify User via DM
```
Use message tool:
- action: send
- target: [user ID from config]
- message: "📋 New task: [ID] - [title]. Starting now..."
```

### 3. Process Task
- Update Linear status → "In Progress" via `./scripts/linear-api.sh start [task-id]`
- Execute the task (spawn sub-agent if complex)
- Save outputs to appropriate location (research/, content/, etc.)

### 4. Complete
- Update Linear status → "Done" via `./scripts/linear-api.sh done [task-id]`
- Add comment with results via `./scripts/linear-api.sh comment [task-id] "[summary]"`
- Send completion DM to user

### 5. Git Sync (if enabled)
```bash
git add [output files]
git commit -m "task: [ID] - [title]"
git push
```

## Script Reference

`scripts/linear-api.sh` commands:

| Command | Description |
|---------|-------------|
| `teams` | List teams and IDs |
| `states` | List workflow states |
| `get [id]` | Get task details |
| `pending` | List pending tasks |
| `start [id]` | Mark as In Progress |
| `done [id]` | Mark as Done |
| `comment [id] "text"` | Add comment to task |

## Example Task Types

This workflow handles any task type:

- **Research**: Spawn sub-agent, save to `research/[topic].md`
- **Content creation**: Generate drafts, save to `content/`
- **Code tasks**: Write/modify code, commit changes
- **Data processing**: Run scripts, output results
- **Custom**: Define your own output patterns

## Troubleshooting

**Tasks not triggering?**
- Check Pipedream workflow is enabled
- Verify Discord channel is in Clawdbot config
- Ensure `allowBots: true` if using webhook

**Linear API errors?**
- Verify API key in `~/.clawdbot/linear.env`
- Check team/state IDs are correct

**Git push failing?**
- Ensure git remote is configured
- Check SSH key or credentials
