# Zapier Setup Guide

Step-by-step guide to connect Linear → Discord via Zapier.

> ⚠️ **Paid Plan Required:** Zapier free plan does not include webhooks or instant triggers. You need **Zapier Starter ($19.99/mo)** or higher for real-time Linear integration. If you're on free tier, use Pipedream instead.

## Create Zap

1. Go to [zapier.com](https://zapier.com) and sign in
2. Click **Create Zap**
3. Name it "Linear to Discord"

## Step 1: Trigger - Linear

1. Search for **Linear** app
2. Choose **New Issue** as trigger event
3. Connect your Linear account (OAuth)
4. Select your workspace and team
5. Test trigger to confirm connection

## Step 2: Action - Discord

1. Click **+** to add action
2. Search for **Discord**
3. Choose **Send Channel Message**
4. Connect your Discord bot:
   - Use **Webhooks by Zapier** for simpler setup, OR
   - Use **Discord Bot** integration with your Clawdbot token

### Option A: Discord Webhook (Simpler)

1. In Discord, go to your #linear-tasks channel
2. Edit Channel → Integrations → Webhooks → New Webhook
3. Copy webhook URL
4. In Zapier, use **Webhooks by Zapier** → **POST**
5. URL: Your Discord webhook URL
6. Payload:
```json
{
  "content": "<@YOUR_BOT_ID>\n📋 New task: {{title}}\n  Status: {{state_name}}\n  ID: {{identifier}}"
}
```

### Option B: Discord Bot (Direct)

1. In Zapier, choose Discord → Send Channel Message
2. Connect using Clawdbot's bot token
3. Channel: Your #linear-tasks channel
4. Message:
```
<@YOUR_BOT_ID>
📋 New task: {{1. Title}}
  Status: {{1. State Name}}
  ID: {{1. Identifier}}
```

## Step 3: Turn On

1. Test the Zap
2. Click **Publish** or **Turn On**

## Field Mapping Reference

Linear fields available in Zapier:

| Zapier Field | Description |
|--------------|-------------|
| `{{1. Title}}` | Task title |
| `{{1. Identifier}}` | Task ID (e.g., BAG-12) |
| `{{1. Description}}` | Task description |
| `{{1. State Name}}` | Current status |
| `{{1. Priority}}` | Priority level |
| `{{1. URL}}` | Link to task in Linear |

## Filters (Recommended)

Add filters to reduce noise and only process tasks ready for Clawdbot.

### Filter: Task Status = Todo

1. Add **Filter by Zapier** between trigger and action
2. Condition: `State Name` exactly matches `Todo`

**Why this matters:**
- Ignores tasks still in Backlog (not ready)
- Only fires when task is in "Todo" = ready for processing
- Prevents wasted Zapier tasks on irrelevant events

### For Task Updates (Optional Zap)

If you create a separate Zap for "Issue Updated in Linear":

1. Add Filter: `State Name` exactly matches `Todo`
2. This catches tasks moved to Todo from Backlog

**Recommended workflow:** Drag task to "Todo" in Linear → Clawdbot picks it up.

## Test

1. Create a new task in Linear
2. Check Zapier task history
3. Verify message appears in Discord
4. Confirm Clawdbot responds

## Troubleshooting

### Zap not triggering
- Check Zap is turned on
- Verify Linear account is connected
- Check Zapier task history for errors

### Discord message not sending
- Verify webhook URL or bot token
- Check bot has channel permissions
- Test webhook with curl first

### Rate limits
- Free Zapier: 100 tasks/month
- Consider batching or upgrading if heavy usage
