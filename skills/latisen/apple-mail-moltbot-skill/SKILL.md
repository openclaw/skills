---
name: apple-mail
description: Read and interact with Apple Mail via osascript on macOS. Use when you need to: (1) List mail accounts, (2) List mailboxes/folders for an account, (3) Get messages from a specific mailbox, (4) Read message content. Works with Apple Mail app on macOS only.
metadata: {"moltbot":{"emoji":"📧","os":["darwin"],"requires":{"bins":["osascript"]}}}
---

# Apple Mail Skill

## Overview

This skill enables interaction with Apple Mail on macOS through AppleScript (osascript). It provides capabilities to list accounts, browse mailboxes, retrieve message lists, and read full message content.

## Prerequisites

- macOS system
- Apple Mail app installed and configured
- At least one mail account set up in Apple Mail
- Apple Mail must be running when using this skill

## Quick Start

### List Available Accounts

```bash
python3 {baseDir}/scripts/list_accounts.py
```

### List Mailboxes for an Account

```bash
python3 {baseDir}/scripts/list_mailboxes.py "Account Name"
```

### Get Messages from a Mailbox

```bash
# Get 10 most recent messages (default)
python3 {baseDir}/scripts/get_messages.py "Account Name" "INBOX"

# Get specific number of messages
python3 {baseDir}/scripts/get_messages.py "Account Name" "INBOX" --limit 20
```

### Read Full Message Content

```bash
python3 {baseDir}/scripts/get_message_content.py "MESSAGE_ID"
```

## Typical Workflows

### Workflow 1: Browse Mail

1. List accounts to see what's available
2. Choose an account and list its mailboxes
3. Get messages from desired mailbox
4. Read full content of specific messages

### Workflow 2: Search for Specific Messages

1. Get messages from target mailbox with appropriate limit
2. Review subjects and senders from the list
3. Identify message IDs of interest
4. Read full content of relevant messages

## Script Reference

### `list_accounts.py`

Lists all configured mail accounts in Apple Mail.

**Output format:** JSON array of account names
```json
{
  "accounts": ["iCloud", "Gmail", "Work"],
  "count": 3
}
```

### `list_mailboxes.py <account_name>`

Lists all mailboxes (folders) for a specific account.

**Arguments:**
- `account_name`: Name of the mail account (from list_accounts.py)

**Output format:** JSON array of mailbox names
```json
{
  "account": "iCloud",
  "mailboxes": ["INBOX", "Sent", "Drafts", "Trash", "Archive"],
  "count": 5
}
```

### `get_messages.py <account_name> <mailbox_name> [--limit N]`

Retrieves message list from a specific mailbox.

**Arguments:**
- `account_name`: Name of the mail account
- `mailbox_name`: Name of the mailbox (e.g., "INBOX", "Sent")
- `--limit N`: Optional, max number of messages to retrieve (default: 10)

**Output format:** JSON array with message metadata
```json
{
  "account": "iCloud",
  "mailbox": "INBOX",
  "messages": [
    {
      "id": "123456",
      "subject": "Meeting Tomorrow",
      "sender": "colleague@example.com",
      "date_sent": "Monday, January 27, 2026 at 10:30:00 AM",
      "date_received": "Monday, January 27, 2026 at 10:30:05 AM",
      "read_status": false,
      "message_size": 2048
    }
  ],
  "count": 1
}
```

### `get_message_content.py <message_id>`

Retrieves full content of a specific message.

**Arguments:**
- `message_id`: Message ID from get_messages.py output

**Output format:** JSON with full message details
```json
{
  "subject": "Meeting Tomorrow",
  "sender": "colleague@example.com",
  "content": "Hi, let's meet tomorrow at 2 PM...",
  "date_sent": "Monday, January 27, 2026 at 10:30:00 AM"
}
```

## Common Patterns

### Pattern: Find Unread Messages

1. Get messages from INBOX
2. Filter results where `read_status` is `false`
3. Read content of unread messages

### Pattern: Check Sent Messages

1. List mailboxes to find "Sent" or "Sent Messages"
2. Get messages from sent mailbox
3. Review what was sent recently

### Pattern: Search Multiple Mailboxes

1. List all mailboxes for account
2. Iterate through mailboxes of interest
3. Get messages from each
4. Aggregate and present results

## Error Handling

All scripts output errors in a consistent format:

```json
{
  "error": "Error description",
  "details": "Additional context if available"
}
```

Common errors:
- **Apple Mail not running**: Start the Mail app
- **Invalid account name**: Check spelling, account names are case-sensitive
- **Invalid mailbox name**: Use exact name from list_mailboxes.py
- **Message not found**: Message may have been deleted or moved

## Important Notes

- **Case sensitivity**: Account and mailbox names are case-sensitive
- **Mail app must be running**: All scripts require Apple Mail to be open
- **Permissions**: First use may prompt for automation permissions in System Preferences
- **Performance**: Large mailboxes may take longer to query; use --limit to constrain results
- **Message IDs**: Message IDs are persistent unless the message is deleted

## Limitations

- Only works on macOS
- Requires Apple Mail (doesn't work with other mail clients)
- Cannot send or delete messages (read-only operations)
- Cannot modify message properties (flags, folders, etc.)
- Limited to mailboxes directly under accounts (nested folders may not be accessible)
