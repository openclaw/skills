# AgentMail Common Patterns

## Newsletter Subscription Automation

Automatically subscribe an inbox to newsletters and process incoming emails.

```python
import os
from agentmail import AgentMail

client = AgentMail(api_key=os.getenv('AGENTMAIL_API_KEY'))

# Create dedicated inbox for newsletters
newsletter_inbox = client.inboxes.create()
print(f"Newsletter inbox: {newsletter_inbox.inbox_id}")

# Subscribe to newsletters (example URLs)
subscriptions = [
    {"url": "https://example.com/subscribe", "email": newsletter_inbox.inbox_id}
]

# Process incoming newsletters
for message in client.inboxes.messages.watch(newsletter_inbox.inbox_id):
    if "unsubscribe" in message.text.lower():
        continue  # Skip unsubscribe confirmations
    
    # Extract content and save
    content = {
        'subject': message.subject,
        'from': message.from_,
        'date': message.date,
        'body': message.text
    }
    
    # Save to file
    save_newsletter(content)
    
    # Optionally send summary to main inbox
    client.inboxes.messages.send(
        inbox_id=main_inbox.inbox_id,
        to=main_inbox.inbox_id,
        subject=f"Newsletter: {message.subject}",
        text=f"New newsletter from {message.from_}\n\nPreview: {message.text[:200]}..."
    )
```

## Email-to-Task Workflow

Convert incoming emails to tasks in your task manager.

```python
import re

for message in client.inboxes.messages.watch(inbox_id):
    # Extract task info
    subject = message.subject
    
    # Check for task markers
    if subject.startswith("[TASK]"):
        task_title = subject.replace("[TASK]", "").strip()
        task_body = message.text
        
        # Create task in your system
        create_task(
            title=task_title,
            description=task_body,
            source_email=message.message_id
        )
        
        # Send confirmation
        client.inboxes.messages.reply(
            inbox_id=inbox_id,
            message_id=message.message_id,
            text=f"Task created: {task_title}\n\nID: {task_id}"
        )
```

## Human-in-the-Loop Approval

Send emails requiring human approval before taking action.

```python
def send_for_approval(action_details, approver_email, agent_inbox):
    """Send action for human approval."""
    
    message = client.inboxes.messages.send(
        inbox_id=agent_inbox,
        to=approver_email,
        cc=[agent_inbox],  # Keep agent in loop
        subject=f"[APPROVAL REQUIRED] {action_details['title']}",
        text=f"""Action requires your approval:

{action_details['description']}

Reply with:
- APPROVE to proceed
- REJECT to cancel
- MODIFY: <changes> to adjust

Action ID: {action_details['id']}""",
        labels=['approval-pending', action_details['category']]
    )
    
    return message.message_id

def check_approval_response(inbox_id, original_message_id, timeout_hours=24):
    """Check for approval response."""
    
    messages = client.inboxes.messages.list(inbox_id=inbox_id, limit=50)
    
    for msg in messages:
        if msg.in_reply_to == original_message_id:
            text = msg.text.upper()
            
            if "APPROVE" in text:
                return "approved"
            elif "REJECT" in text:
                return "rejected"
            elif "MODIFY" in text:
                # Extract modifications
                modifications = text.split("MODIFY:", 1)[-1].strip()
                return ("modify", modifications)
    
    return "pending"
```

## Attachment Processing Pipeline

Process incoming attachments automatically.

```python
import os
from pathlib import Path

def process_attachments(inbox_id, download_dir="downloads"):
    """Download and process all attachments from new messages."""
    
    download_path = Path(download_dir)
    download_path.mkdir(exist_ok=True)
    
    for message in client.inboxes.messages.watch(inbox_id):
        if not message.attachments:
            continue
        
        for att in message.attachments:
            # Download attachment
            content = client.attachments.download(att.attachment_id)
            
            # Save to file
            file_path = download_path / att.filename
            file_path.write_bytes(content)
            
            # Process based on type
            if att.filename.endswith('.pdf'):
                text = extract_pdf_text(file_path)
                save_extracted_text(message.message_id, text)
            
            elif att.filename.endswith(('.jpg', '.png')):
                process_image(file_path)
            
            elif att.filename.endswith('.csv'):
                import_csv_to_database(file_path)
```

## Multi-Inbox Load Balancing

Distribute email sending across multiple inboxes for better deliverability.

```python
import random

class InboxPool:
    """Manage a pool of inboxes for load balancing."""
    
    def __init__(self, client, pool_size=5):
        self.client = client
        self.inboxes = []
        
        # Create pool of inboxes
        for _ in range(pool_size):
            inbox = client.inboxes.create()
            self.inboxes.append(inbox.inbox_id)
    
    def get_random_inbox(self):
        """Get random inbox from pool."""
        return random.choice(self.inboxes)
    
    def send_distributed(self, recipients, subject, body):
        """Send emails distributed across pool."""
        results = []
        
        for recipient in recipients:
            inbox = self.get_random_inbox()
            
            message = self.client.inboxes.messages.send(
                inbox_id=inbox,
                to=recipient,
                subject=subject,
                text=body
            )
            
            results.append({
                'recipient': recipient,
                'inbox': inbox,
                'message_id': message.message_id
            })
        
        return results

# Usage
pool = InboxPool(client, pool_size=10)
results = pool.send_distributed(
    recipients=['user1@example.com', 'user2@example.com', ...],
    subject='Bulk notification',
    body='Message content'
)
```

## Email Digest Summary

Send daily/weekly digest of collected information.

```python
from datetime import datetime, timedelta

def send_digest(inbox_id, recipient, period='daily'):
    """Send digest of recent emails."""
    
    # Calculate time window
    if period == 'daily':
        since = datetime.now(timezone.utc) - timedelta(days=1)
    elif period == 'weekly':
        since = datetime.now(timezone.utc) - timedelta(weeks=1)
    
    # Get messages
    messages = client.inboxes.messages.list(inbox_id=inbox_id, limit=100)
    
    # Filter by date
    recent = [m for m in messages 
              if m.date and m.date > since]
    
    # Build digest
    digest_lines = [f"# {period.title()} Digest - {len(recent)} messages\n"]
    
    for msg in recent:
        digest_lines.append(f"\n## {msg.subject}")
        digest_lines.append(f"From: {msg.from_}")
        digest_lines.append(f"Preview: {msg.text[:200]}...")
        digest_lines.append(f"Link: https://x.com/msg/{msg.message_id}")
    
    digest_text = "\n".join(digest_lines)
    
    # Send digest
    client.inboxes.messages.send(
        inbox_id=inbox_id,
        to=recipient,
        subject=f"[{period.title()} Digest] {len(recent)} new messages",
        text=digest_text
    )
```

## Auto-Responder with Context

Smart auto-responder that understands conversation context.

```python
from collections import defaultdict

# Store conversation context
conversation_context = defaultdict(list)

def smart_responder(inbox_id):
    """Auto-respond to emails with context awareness."""
    
    for message in client.inboxes.messages.watch(inbox_id):
        thread_id = message.thread_id
        
        # Update context
        conversation_context[thread_id].append({
            'role': 'user',
            'content': message.text,
            'timestamp': message.date
        })
        
        # Generate contextual response
        context = conversation_context[thread_id]
        response_text = generate_response(context, message.text)
        
        # Send reply
        reply = client.inboxes.messages.reply(
            inbox_id=inbox_id,
            message_id=message.message_id,
            text=response_text
        )
        
        # Update context with response
        conversation_context[thread_id].append({
            'role': 'assistant',
            'content': response_text,
            'timestamp': reply.date
        })
```

## Error Recovery & Retry

Handle failures gracefully with retry logic.

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """Decorator for retry logic."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3)
def send_email_with_retry(client, **kwargs):
    """Send email with automatic retry."""
    return client.inboxes.messages.send(**kwargs)

# Usage
result = send_email_with_retry(
    client,
    inbox_id='sender@agentmail.to',
    to='recipient@example.com',
    subject='Important',
    text='Message content'
)
```
