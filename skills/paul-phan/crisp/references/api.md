# Crisp REST API Reference

## Base URL
```
https://api.crisp.chat/v1/website/{website_id}
```

## Authentication
```
Authorization: Basic <base64(token_identifier:token_key)>
X-Crisp-Tier: plugin
```

Set via environment variables:
- `CRISP_WEBSITE_ID` - Website ID (used in URL)
- `CRISP_TOKEN_ID` - Plugin Token Identifier (used in Auth)
- `CRISP_TOKEN_KEY` - Plugin Token Key (used in Auth)

## Key Endpoints

### Conversations

#### List Conversations
```
GET /v1/website/{website_id}/conversations/{page_number}
```

Query Parameters:
- `per_page` (20-50, default: 20)
- `search_query` - Search text
- `search_type` - "text", "segment", or "filter"
- `filter_unread` (0/1) - Only unread
- `filter_not_resolved` (0/1) - Only unresolved
- `filter_resolved` (0/1) - Only resolved
- `filter_assigned` - Only assigned to user ID
- `filter_unassigned` (0/1) - Only unassigned
- `filter_mention` (0/1) - Only where mentioned
- `order_date_updated` (0/1) - Sort by update time

Response: Array of conversation objects

#### Get Conversation
```
GET /v1/website/{website_id}/conversation/{session_id}
```

Response: Conversation object with:
- `session_id` - Unique ID
- `state` - "pending", "unresolved", "resolved"
- `meta` - Visitor info (nickname, email, phone, etc.)
- `meta.email` - Visitor email (verified)
- `last_message` - Latest message excerpt
- `updated_at` - Last update timestamp
- `created_at` - Creation timestamp

#### Update Conversation Meta
```
PATCH /v1/website/{website_id}/conversation/{session_id}/meta
```

Body: `{ "state": "resolved" }` or `{ "state": "unresolved" }`

### Messages

#### Get Messages
```
GET /v1/website/{website_id}/conversation/{session_id}/messages
```

Query Parameters:
- `timestamp_before` - Paginate from this timestamp

Response: Array of message objects with:
- `type` - "text", "note", "file", "audio", etc.
- `from` - "user" or "operator"
- `content` - Message content (string or object)
- `timestamp` - When sent
- `edited` - Whether edited
- `read` - Delivery status ("chat", "email", "urn:*")

#### Send Message
```
POST /v1/website/{website_id}/conversation/{session_id}/message
```

Body:
```json
{
  "type": "text",
  "content": "Your message here",
  "from": "operator"
}
```

#### Mark as Read
```
PATCH /v1/website/{website_id}/conversation/{session_id}/read
```

Body:
```json
{
  "from": "operator"
  "read": true
}
```

## Conversation States

| State | Status | Description |
|--------|---------|-------------|
| pending | 0 | New conversation, no activity |
| unresolved | 1 | Active conversation |
| resolved | 2 | Closed conversation |

## Visitor Metadata

Available in `conversation.meta`:
- `nickname` - Display name
- `email` - Verified email (may be empty)
- `phone` - Phone number
- `subject` - Conversation subject (if set)
- `origin` - "chat", "email", or "urn:*"
- `ip` - Visitor IP address
- `device` - Browser, OS, geolocation
- `timezone` - UTC offset
