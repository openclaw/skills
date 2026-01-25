---
name: clippy
description: Microsoft 365 / Outlook CLI for calendar and email. Use when managing Outlook calendar (view, create, update, delete events, find meeting times, respond to invitations), sending/reading emails, or searching for people/rooms in the organization.
metadata: {"clawdbot":{"requires":{"bins":["clippy"]}}}
---

# Clippy - Microsoft 365 CLI

Source: https://github.com/foeken/clippy

Works through the M365 web UI via browser automation (Playwright), not the Graph API. No Azure AD app registration required - just login with your browser.

## Install

```bash
git clone https://github.com/foeken/clippy.git
cd clippy && bun install
bun run src/cli.ts --help
```

Or link globally: `bun link`

## Authentication

```bash
# Interactive login (opens browser, establishes session)
clippy login --interactive

# Check auth status
clippy whoami
```

### Keepalive (recommended)

Keep a browser session alive to prevent token expiry:

```bash
# Start keepalive (keeps browser open, refreshes every 10min)
clippy keepalive --interval 10
```

For persistent operation, set up as a launchd service (macOS) or systemd (Linux).

**Health monitoring:** Keepalive writes to `~/.config/clippy/keepalive-health.txt` on each successful refresh. Check if this file is stale (>15min) to detect failures.

## Calendar

```bash
# Today's events
clippy calendar

# Specific day
clippy calendar --day tomorrow
clippy calendar --day monday
clippy calendar --day 2024-02-15

# Week view
clippy calendar --week

# With details (description, attendees)
clippy calendar --details
```

### Create Events

```bash
clippy create-event "Title" 09:00 10:00

# Full options
clippy create-event "Meeting" 14:00 15:00 \
  --day tomorrow \
  --description "Meeting notes" \
  --attendees "alice@company.com,bob@company.com" \
  --teams \
  --find-room

# Recurring
clippy create-event "Standup" 09:00 09:15 --repeat daily
clippy create-event "Sync" 14:00 15:00 --repeat weekly --days mon,wed,fri
```

### Update/Delete Events

```bash
clippy update-event 1 --title "New Title"
clippy update-event 1 --start 10:00 --end 11:00
clippy delete-event 1
clippy delete-event 1 --message "Need to reschedule"
```

### Respond to Invitations

```bash
clippy respond                           # List pending
clippy respond accept --id <eventId>
clippy respond decline --id <eventId> --message "Conflict"
clippy respond tentative --id <eventId>
```

### Find Meeting Times

```bash
clippy findtime
clippy findtime --attendees "alice@company.com,bob@company.com"
clippy findtime --duration 60 --days 5
```

## Email

```bash
# Inbox
clippy mail
clippy mail --unread
clippy mail -n 20
clippy mail --search "invoice"

# Other folders
clippy mail sent
clippy mail drafts
clippy mail archive

# Read email
clippy mail -r <number>

# Download attachments
clippy mail -d <number> -o ~/Downloads
```

### Send Email

```bash
clippy send \
  --to "recipient@example.com" \
  --subject "Subject" \
  --body "Message body"

# With CC, attachments, markdown
clippy send \
  --to "alice@example.com" \
  --cc "manager@example.com" \
  --subject "Report" \
  --body "**See attached**" \
  --markdown \
  --attach "report.pdf"
```

### Reply/Forward

```bash
clippy mail --reply <number> --message "Thanks!"
clippy mail --reply-all <number> --message "Got it"
clippy mail --forward <number> --to-addr "colleague@example.com"
```

### Email Actions

```bash
clippy mail --mark-read <number>
clippy mail --flag <number>
clippy mail --move <number> --to archive
```

## People/Room Search

```bash
clippy find "john"                       # People
clippy find "conference" --rooms         # Rooms
```

## JSON Output

```bash
clippy calendar --json
clippy mail --json
```

## Configuration

Profile directory can be overridden:
```bash
export CLIPPY_PROFILE_DIR=~/.config/clippy/my-profile
```
