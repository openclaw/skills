# WeCom MCP Server for Clawdbot

Send messages to WeCom (企业微信) via incoming webhooks.

## Installation

```bash
# Set your webhook URL
export WECOM_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"

# Install globally
npm install -g wecom-bot-mcp-server

# Or run directly with npx
npx wecom-bot-mcp-server
```

## Available Tools

### send_wecom_message

Send a text message to WeCom channel.

```json
{
  "type": "function",
  "function": {
    "name": "send_wecom_message",
    "description": "Send a text message to WeCom via webhook",
    "parameters": {
      "type": "object",
      "properties": {
        "content": {
          "type": "string",
          "description": "Message content to send"
        },
        "mentioned_list": {
          "type": "array",
          "description": "List of userids to mention",
          "items": {"type": "string"}
        }
      },
      "required": ["content"]
    }
  }
}
```

### send_wecom_markdown

Send a markdown message to WeCom channel.

```json
{
  "type": "function",
  "function": {
    "name": "send_wecom_markdown",
    "description": "Send a markdown message to WeCom via webhook",
    "parameters": {
      "type": "object",
      "properties": {
        "content": {
          "type": "string",
          "description": "Markdown content to send"
        }
      },
      "required": ["content"]
    }
  }
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `WECOM_WEBHOOK_URL` | Yes | WeCom incoming webhook URL |
| `WECOM_TIMEOUT_MS` | No | Request timeout in ms (default: 10000) |

## WeCom Markdown Support

WeCom supports a subset of Markdown:

- **Bold**: `<strong>text</strong>` or `**text**`
- *Italic*: `<i>text</i>` or `*text*`
- ~~Strikethrough~~: `<s>text</s>`
- Links: `<a href="url">text</a>`
- Images: `<img src="url" />`
- Headers: `<font size="5">text</font>`

## Examples

```typescript
import { sendWecomMessage } from 'wecom-bot-mcp-server';

// Send simple text
await sendWecomMessage({
  content: "Hello from Clawdbot!"
});

// Send with mentions
await sendWecomMessage({
  content: "Meeting starting now",
  mentioned_list: ["zhangsan", "lisi"]
});

// Send markdown
await sendWecomMarkdown({
  content: "# Daily Report\n\n**Completed:**\n- Task A\n- Task B\n\n**Pending:**\n- Task C"
});
```
