# AgentMail Examples

## Basic Email Sending

### Simple Text Email
```python
from agentmail import AgentMail
import os

client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))

# Create inbox
inbox = client.inboxes.create()

# Send simple email
message = client.inboxes.messages.send(
    inbox_id=inbox.inbox_id,
    to="friend@example.com",
    subject="Hello",
    text="This is a test email from my agent."
)

print(f"Sent: {message.message_id}")
```

### HTML Email with Attachments
```python
import base64
from pathlib import Path

# Read attachment
pdf_path = Path("document.pdf")
pdf_content = pdf_path.read_bytes()

# Send HTML email with attachment
message = client.inboxes.messages.send(
    inbox_id=inbox.inbox_id,
    to="recipient@example.com",
    subject="Report",
    text="Please find the attached report.",
    html="""
    <html>
    <body>
        <h1>Monthly Report</h1>
        <p>Please find the attached report.</p>
    </body>
    </html>
    """,
    attachments=[
        SendAttachment(
            filename="report.pdf",
            content=base64.b64encode(pdf_content).decode()
        )
    ]
)
```

## Inbox Management

### Create Multiple Inboxes
```python
# Create dedicated inboxes for different purposes
inboxes = {
    'support': client.inboxes.create(username="support"),
    'newsletters': client.inboxes.create(username="newsletters"),
    'notifications': client.inboxes.create(username="notifications")
}

for purpose, inbox in inboxes.items():
    print(f"{purpose}: {inbox.inbox_id}")
```

### Cleanup Old Inboxes
```python
# Delete inboxes older than 30 days
from datetime import datetime, timedelta

cutoff = datetime.now(timezone.utc) - timedelta(days=30)
response = client.inboxes.list()

for inbox in response.inboxes:
    if inbox.created_at < cutoff:
        client.inboxes.delete(inbox.inbox_id)
        print(f"Deleted: {inbox.inbox_id}")
```

## Email Processing

### Auto-Responder
```python
import time

def auto_responder(inbox_id, allowed_senders):
    """Auto-respond to emails from allowed senders."""
    
    for message in client.inboxes.messages.watch(inbox_id):
        # Security check
        if message.from_ not in allowed_senders:
            print(f"Ignored: {message.from_}")
            continue
        
        # Generate response
        response_text = f"Thanks for your email: '{message.subject}'"
        
        # Send reply
        client.inboxes.messages.reply(
            inbox_id=inbox_id,
            message_id=message.message_id,
            text=response_text
        )
        
        print(f"Replied to: {message.from_}")

# Usage
auto_responder(
    inbox_id="my-agent@agentmail.to",
    allowed_senders=["trusted@example.com"]
)
```

### Email-to-Slack Bridge
```python
import requests

SLACK_WEBHOOK = "https://hooks.slack.com/services/..."

def forward_to_slack(message):
    """Forward important emails to Slack."""
    
    payload = {
        "text": f"📧 Email from {message.from_}",
        "attachments": [{
            "title": message.subject,
            "text": message.text[:500],
            "footer": f"{message.inbox_id}"
        }]
    }
    
    requests.post(SLACK_WEBHOOK, json=payload)

# Watch and forward
for message in client.inboxes.messages.watch("alerts@agentmail.to"):
    if "URGENT" in message.subject:
        forward_to_slack(message)
```

## Webhook Integration

### Flask Webhook Handler
```python
from flask import Flask, request, jsonify

app = Flask(__name__)
ALLOWLIST = ['trusted@example.com']

@app.route('/webhook/agentmail', methods=['POST'])
def handle_email():
    payload = request.json
    message = payload.get('message', {})
    
    # Security: Check sender
    sender = message.get('from')
    if sender not in ALLOWLIST:
        return jsonify({'status': 'blocked'}), 403
    
    # Process email
    process_email(message)
    
    return jsonify({'status': 'ok'}), 200

def process_email(message):
    """Process incoming email."""
    print(f"Processing: {message['subject']}")
    # Add your logic here

if __name__ == '__main__':
    app.run(port=5000)
```

### Register Webhook
```python
# Register webhook endpoint
webhook = client.webhooks.create(
    url="https://your-domain.com/webhook/agentmail",
    client_id="email-processor",
    events=['message.received']
)

print(f"Webhook ID: {webhook.id}")
```

## Newsletter Management

### Subscribe to Newsletters
```python
# Create dedicated inbox
newsletter_inbox = client.inboxes.create(username="newsletters")

# Subscribe to various newsletters
subscriptions = [
    {"service": "TechCrunch", "email": newsletter_inbox.inbox_id},
    {"service": "ProductHunt", "email": newsletter_inbox.inbox_id},
]

# Process incoming newsletters
for message in client.inboxes.messages.watch(newsletter_inbox.inbox_id):
    if message.from_ in NEWSLETTER_SENDERS:
        save_newsletter_summary(message)
```

### Weekly Digest
```python
from datetime import datetime, timedelta

def send_weekly_digest(inbox_id, recipient):
    """Send weekly digest of emails."""
    
    # Get emails from last 7 days
    since = datetime.now(timezone.utc) - timedelta(days=7)
    messages = client.inboxes.messages.list(inbox_id=inbox_id, limit=50)
    
    recent = [m for m in messages if m.date > since]
    
    # Build digest
    lines = [f"Weekly Digest: {len(recent)} emails\n"]
    for msg in recent:
        lines.append(f"• {msg.from_}: {msg.subject}")
    
    digest_text = "\n".join(lines)
    
    # Send digest
    client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=recipient,
        subject="[Weekly Digest] Your email summary",
        text=digest_text
    )
```

## Error Handling

### Retry with Backoff
```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

@retry(max_attempts=3)
def send_with_retry(client, **kwargs):
    return client.inboxes.messages.send(**kwargs)
```

### Graceful Degradation
```python
def safe_send_email(client, **kwargs):
    """Send email with fallback options."""
    
    try:
        # Try primary inbox
        return client.inboxes.messages.send(**kwargs)
    except LimitExceededError:
        # Create new inbox if limit reached
        new_inbox = client.inboxes.create()
        kwargs['inbox_id'] = new_inbox.inbox_id
        return client.inboxes.messages.send(**kwargs)
    except Exception as e:
        # Log and queue for retry
        queue_for_retry(kwargs)
        raise
```

## Testing

### Mock Client for Testing
```python
from unittest.mock import Mock

def create_mock_client():
    """Create mock AgentMail client for testing."""
    
    mock = Mock()
    
    # Mock inbox
    mock_inbox = Mock()
    mock_inbox.inbox_id = "test@agentmail.to"
    mock.inboxes.create.return_value = mock_inbox
    
    # Mock message
    mock_message = Mock()
    mock_message.message_id = "msg_123"
    mock.inboxes.messages.send.return_value = mock_message
    
    return mock

# Usage in tests
def test_email_sending():
    client = create_mock_client()
    
    message = client.inboxes.messages.send(
        inbox_id="test@agentmail.to",
        to="user@example.com",
        subject="Test",
        text="Hello"
    )
    
    assert message.message_id == "msg_123"
```
