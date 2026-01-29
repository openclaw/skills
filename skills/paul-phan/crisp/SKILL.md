---
name: crisp
description: Customer support via Crisp API. Use when the user asks to check, read, search, or respond to Crisp inbox messages. Requires Crisp website ID and plugin token (authenticated via environment variables CRISP_WEBSITE_ID, CRISP_TOKEN_ID, and CRISP_TOKEN_KEY).
---

# Crisp Customer Support

Crisp is a customer support platform. Use this skill when the user needs to:
- Check for new messages in the inbox
- Read conversation history
- Search conversations
- Send replies to customers
- Check conversation status

## Credentials

Crisp requires authentication via HTTP headers with a token identifier and key (Basic Auth), plus the website ID for the API URL.

Set these as environment variables (stored securely, never logged):
- `CRISP_WEBSITE_ID` - Your website identifier (e.g., `0f4c...`)
- `CRISP_TOKEN_ID` - Your Plugin Token Identifier (e.g., `e47d...`)
- `CRISP_TOKEN_KEY` - Your Plugin Token Key (e.g., `a7d7...`)

## Common Workflows

### Check Inbox Status
```bash
scripts/crisp.py inbox list --page 1
```

### Read Conversation
```bash
scripts/crisp.py conversation get <session_id>
```

### Get Messages in Conversation
```bash
scripts/crisp.py messages get <session_id>
```

### Send a Reply
```bash
scripts/crisp.py message send <session_id> "Your reply text here"
```

### Search Conversations
```bash
scripts/crisp.py conversations search "query terms" --filter unresolved --max 10
```

### Mark as Read
```bash
scripts/crisp.py conversation read <session_id>
```

### Resolve Conversation
```bash
scripts/crisp.py conversation resolve <session_id>
```

## API Reference

Key endpoints used:
- `GET /v1/website/{website_id}/conversations/{page}` - List conversations
- `GET /v1/website/{website_id}/conversation/{session_id}` - Get conversation details
- `GET /v1/website/{website_id}/conversation/{session_id}/messages` - Get messages
- `POST /v1/website/{website_id}/conversation/{session_id}/message` - Send message
- `PATCH /v1/website/{website_id}/conversation/{session_id}/read` - Mark as read
- `PATCH /v1/website/{website_id}/conversation/{session_id}` - Update/resolve

Base URL: `https://api.crisp.chat`

## Notes

- Always ask before sending customer replies to confirm tone/content
- Check for `meta.email` in conversation for customer email
- Verify `CRISP_WEBSITE_ID`, `CRISP_TOKEN_ID`, and `CRISP_TOKEN_KEY` are set before running commands
- Use `--json` flag for script output when parsing programmatically
