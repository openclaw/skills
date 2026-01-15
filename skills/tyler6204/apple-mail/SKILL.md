---
name: apple-mail
description: Apple Mail.app integration for macOS. Read inbox, search emails, send emails, reply, and manage messages.
metadata: {"clawdbot":{"emoji":"📧","os":["darwin"],"requires":{"bins":["sqlite3"]}}}
---

# Apple Mail

Interact with Mail.app via AppleScript. Run scripts from: `cd {baseDir}`

## Commands

| Command | Usage |
|---------|-------|
| List recent | `scripts/mail-list.sh [mailbox] [account] [limit]` |
| Search | `scripts/mail-search.sh "query" [mailbox] [limit]` |
| Read email | `scripts/mail-read.sh <message-id>` |
| Send | `scripts/mail-send.sh "to@email.com" "Subject" "Body" [from-account] [attachment]` |
| Reply | `scripts/mail-reply.sh <message-id> "body" [reply-all]` |
| List accounts | `scripts/mail-accounts.sh` |
| List mailboxes | `scripts/mail-mailboxes.sh [account]` |

## Output Format

List/search returns: `ID | ReadStatus | Date | Sender | Subject`
- `●` = unread, blank = read

## Gmail Mailboxes

⚠️ Gmail special folders need `[Gmail]/` prefix:

| Shows as | Use |
|----------|-----|
| `Spam` | `[Gmail]/Spam` |
| `Sent Mail` | `[Gmail]/Sent Mail` |
| `All Mail` | `[Gmail]/All Mail` |
| `Trash` | `[Gmail]/Trash` |

Custom labels work without prefix.

## Fast Search (SQLite)

⚠️ **Quit Mail.app first** — SQLite access while running can corrupt database.

```bash
scripts/mail-fast-search.sh "query" [limit]  # ~50ms vs minutes
```

Only use when Mail is closed. Script refuses to run if Mail is open.

## Errors

| Error | Cause |
|-------|-------|
| `Message not found` | Invalid/deleted ID — get fresh from mail-list.sh |
| `Can't get mailbox` | Invalid name — check mail-mailboxes.sh |
| `Can't get account` | Invalid account — check mail-accounts.sh |

## Notes

- Message IDs are internal, get fresh ones from list/search
- Confirm recipient before sending
- AppleScript search is slow but safe; SQLite is fast but needs Mail quit
