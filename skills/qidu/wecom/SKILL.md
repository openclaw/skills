---
name: wecom
description: "Send messages to WeCom (企业微信) via webhooks using MCP protocol. Works with Claude Code, Claude Desktop, and other MCP clients."
---

# WeCom Skill

Send text and markdown messages to WeCom (企业微信) via incoming webhooks.

## Setup

```bash
# Navigate to skill directory
cd skills/wecom

# Install dependencies
npm install

# Build TypeScript
npm run build

# Set webhook URL
export WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
```

## Usage with Claude Code

Add to your `~/.config/claude_code/mcp.json`:

```json
{
  "mcpServers": {
    "wecom": {
      "command": "node",
      "args": ["/path/to/clawdbot/skills/wecom/dist/index.js"],
      "env": {
        "WECOM_WEBHOOK_URL": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
      }
    }
  }
}
```

Then restart Claude Code. You'll have two new tools:

## Tools

### send_wecom_message

Send a text message to WeCom.

```bash
# Simple message
await send_wecom_message({ content: "Hello from Clawdbot!" });

# With mentions
await send_wecom_message({
  content: "Meeting starting now",
  mentioned_list: ["zhangsan", "lisi"]
});
```

### send_wecom_markdown

Send a markdown message (WeCom flavor).

```bash
await send_wecom_markdown({
  content: `# Daily Report
  
**Completed:**
- Task A
- Task B

**Pending:**
- Task C

<@zhangsan>`
});
```

## WeCom Markdown Tags

WeCom supports:

| Feature | Syntax |
|---------|--------|
| Bold | `**text**` or `<strong>text</strong>` |
| Italic | `*text*` or `<i>text</i>` |
| Strikethrough | `~~text~~` or `<s>text</s>` |
| Mention | `<@userid>` |
| Link | `<a href="url">text</a>` |
| Image | `<img src="url" />` |
| Font size | `<font size="5">text</font>` |
| Color | `<font color="#FF0000">text</font>` |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WECOM_WEBHOOK_URL` | Yes | - | WeCom webhook URL |
| `WECOM_TIMEOUT_MS` | No | 10000 | Request timeout (ms) |
