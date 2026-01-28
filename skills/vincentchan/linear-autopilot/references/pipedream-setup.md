# Pipedream Setup Guide

Step-by-step guide to connect Linear → Discord via Pipedream.

## Create Pipedream Workflow

1. Go to [pipedream.com](https://pipedream.com) and sign in
2. Click **New Workflow**
3. Name it "Linear to Discord" or similar

## Step 1: HTTP Webhook Trigger

1. Select **HTTP / Webhook** as trigger
2. Choose **HTTP Requests**
3. Copy the webhook URL (you'll need this for Linear)

## Step 2: Add Filters (Recommended)

Add filters to reduce noise and only process relevant events.

### Filter 1: Action Type

Only trigger on create/update (ignore deletes, archives, etc.):

1. Click **+** to add step
2. Choose **Filter**
3. Condition: `{{steps.trigger.event.body.action}}` is in `create, update`

### Filter 2: Task Status = Todo

Only notify when tasks enter "Todo" status (ready for processing):

1. Click **+** to add another Filter step
2. Condition: `{{steps.trigger.event.body.data.state.name}}` equals `Todo`

**Why this matters:**
- Ignores tasks still in Backlog (not ready)
- Ignores status changes to In Progress/Done (you'll handle those)
- Prevents duplicate notifications when you update the task
- Only fires when a task is moved to "Todo" = ready for Clawdbot

### Combined Logic

With both filters, Clawdbot only gets notified when:
- A new task is created with status "Todo", OR
- An existing task is moved to "Todo" status

This is the cleanest workflow: drag task to "Todo" in Linear → Clawdbot picks it up.

## Step 3: Discord Send Message

1. Click **+** to add step
2. Search for **Discord Bot** → **Send Message**
3. Connect your Discord bot account (use Clawdbot's bot token)
4. Configure:

**Guild:** Select your server (or leave empty for DM)

**Channel:** Your #linear-tasks channel ID

**Message:**
```
<@YOUR_BOT_ID>
📋 New task: {{steps.trigger.event.body.data.title}}
  Status: {{steps.trigger.event.body.data.state.name}}
  ID: {{steps.trigger.event.body.data.identifier}}
```

Replace `YOUR_BOT_ID` with your Clawdbot Discord bot's user ID.

## Step 4: Deploy

1. Click **Deploy** in top right
2. Your workflow is now live

## Configure Linear Webhook

1. Go to Linear → Settings → API → Webhooks
2. Click **New Webhook**
3. Configure:
   - **Label:** "Pipedream Discord"
   - **URL:** Your Pipedream webhook URL
   - **Team:** Select your team
   - **Events:** Check "Issues" (creates/updates)
4. Click **Create Webhook**

## Test

1. Create a new task in Linear
2. Check Pipedream workflow logs
3. Verify message appears in Discord channel
4. Confirm Clawdbot responds

## Troubleshooting

### Webhook not firing
- Check Linear webhook is enabled
- Verify URL is correct
- Check Pipedream workflow is deployed

### Discord message not sending
- Verify bot token is valid
- Check bot has permission to send in channel
- Confirm channel ID is correct

### Wrong data in message
- Check Pipedream step data explorer
- Verify field paths (e.g., `body.data.title` vs `event.data.title`)

## Advanced: Task Updates

To also notify on status changes, add another filter branch:

```
steps.trigger.event.body.action === "update" &&
steps.trigger.event.body.data.state !== steps.trigger.event.body.previousData?.state
```

This sends notifications when task status changes (e.g., moved to Done).
