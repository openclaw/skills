# AgentMail API Reference

## Inboxes

### Create Inbox
```python
inbox = client.inboxes.create(
    username="my-agent",      # Optional: custom username
    client_id="unique-id"     # Optional: for idempotency
)
```

**Returns:** `Inbox` object
- `inbox_id`: Email address
- `display_name`: Display name
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### List Inboxes
```python
response = client.inboxes.list(
    limit=10,                 # Optional: max results
    cursor=None               # Optional: pagination cursor
)
```

**Returns:** `ListInboxesResponse`
- `inboxes`: List of Inbox objects
- `count`: Total count
- `next_page_token`: Cursor for next page

### Get Inbox
```python
inbox = client.inboxes.get(
    inbox_id='address@agentmail.to'
)
```

### Delete Inbox
```python
client.inboxes.delete(
    inbox_id='address@agentmail.to'
)
```

## Messages

### Send Message
```python
message = client.inboxes.messages.send(
    inbox_id='sender@agentmail.to',
    to='recipient@example.com',
    cc=['cc@example.com'],           # Optional
    bcc=['bcc@example.com'],         # Optional
    subject='Subject',
    text='Plain text body',
    html='<html>...</html>',         # Optional
    labels=['tag1', 'tag2'],         # Optional
    attachments=[                    # Optional
        SendAttachment(
            filename='file.pdf',
            content=b'bytes_or_base64'
        )
    ]
)
```

**Returns:** `Message` object
- `message_id`: Unique ID
- `thread_id`: Conversation thread
- `inbox_id`: Sender inbox
- `subject`, `text`, `html`: Content
- `from_`: Sender address
- `to`, `cc`, `bcc`: Recipients
- `attachments`: List of attachments

### List Messages
```python
messages = client.inboxes.messages.list(
    inbox_id='address@agentmail.to',
    limit=10,
    cursor=None
)
```

### Get Message
```python
message = client.inboxes.messages.get(
    inbox_id='address@agentmail.to',
    message_id='msg_id'
)
```

### Reply to Message
```python
reply = client.inboxes.messages.reply(
    inbox_id='address@agentmail.to',
    message_id='original_msg_id',
    text='Reply text',
    html='<html>...</html>',         # Optional
    attachments=[]                    # Optional
)
```

### Watch Messages (WebSocket)
```python
for message in client.inboxes.messages.watch(
    inbox_id='address@agentmail.to'
):
    print(f"New: {message.subject}")
```

## Attachments

### Download Attachment
```python
content = client.attachments.download(
    attachment_id='att_id'
)
# Returns: bytes
```

## Webhooks

### Create Webhook
```python
webhook = client.webhooks.create(
    url='https://example.com/webhook',
    client_id='my-processor',
    events=['message.received', 'message.sent']
)
```

**Events:**
- `message.received` - New email received
- `message.sent` - Email sent
- `message.read` - Email marked as read

### List Webhooks
```python
webhooks = client.webhooks.list()
```

### Delete Webhook
```python
client.webhooks.delete(webhook_id='wh_id')
```

## Data Types

### Inbox
```python
{
    "inbox_id": "user@agentmail.to",
    "display_name": "Display Name",
    "pod_id": "uuid",
    "client_id": "optional-client-id",
    "created_at": datetime,
    "updated_at": datetime
}
```

### Message
```python
{
    "message_id": "msg_uuid",
    "thread_id": "thread_uuid",
    "inbox_id": "user@agentmail.to",
    "subject": "Subject",
    "text": "Plain text",
    "html": "<html>...</html>",
    "from_": "sender@example.com",
    "to": ["recipient@example.com"],
    "cc": [],
    "bcc": [],
    "date": datetime,
    "attachments": [Attachment]
}
```

### Attachment
```python
{
    "attachment_id": "att_uuid",
    "filename": "document.pdf",
    "content_type": "application/pdf",
    "size": 12345
}
```

## Error Handling

Common exceptions:
- `LimitExceededError` - Inbox limit reached
- `AuthenticationError` - Invalid API key
- `NotFoundError` - Resource not found
- `RateLimitError` - Too many requests

```python
from agentmail.errors import LimitExceededError

try:
    inbox = client.inboxes.create()
except LimitExceededError:
    print("Inbox limit reached")
except Exception as e:
    print(f"Error: {e}")
```
