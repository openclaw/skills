---
name: protonmail
description: Read, search, and scan ProtonMail via IMAP bridge (Proton Bridge or hydroxide). Includes daily digest for important emails.
metadata: {"clawdbot":{"emoji":"📧","requires":{"bins":["python3"]}}}
---

# ProtonMail Skill

Access ProtonMail via IMAP using either:
- **Proton Bridge** (official, recommended)
- **hydroxide** (third-party, headless)

## Setup

### Option 1: Proton Bridge (Docker)

```bash
# Pull and run
docker run -d --name=protonmail-bridge \
  -v protonmail:/root \
  -p 143:143 -p 1025:25 \
  --restart=unless-stopped \
  shenxn/protonmail-bridge

# Initial login (interactive)
docker run --rm -it -v protonmail:/root shenxn/protonmail-bridge init
# Then: login → enter credentials → info (shows bridge password) → exit
```

### Option 2: hydroxide (Headless)

```bash
# Install
git clone https://github.com/emersion/hydroxide.git
cd hydroxide && go build ./cmd/hydroxide

# Login
./hydroxide auth your@email.com

# Run as service
./hydroxide serve
```

## Configuration

Create config file at `~/.config/protonmail-bridge/config.env`:

```bash
PROTONMAIL_HOST=127.0.0.1
PROTONMAIL_PORT=143
PROTONMAIL_USER=your@email.com
PROTONMAIL_PASS=your-bridge-password
```

Or set environment variables directly.

## Usage

```bash
# List mailboxes
protonmail.py mailboxes

# Show recent inbox
protonmail.py inbox --limit 10

# Show unread emails
protonmail.py unread

# Search emails
protonmail.py search "keyword"

# Read specific email
protonmail.py read 123
```

## Daily Scan

The `daily-scan.py` script identifies important emails based on:
- Important senders (banks, government, schools)
- Urgent keywords (DE/EN/NL)

Configure important patterns in the script or via environment variables.

## Sieve Filters (ProtonMail)

Recommended Sieve filter for auto-sorting:

```sieve
require ["fileinto", "imap4flags"];

# Important emails - flag them
if anyof (
    address :contains "From" ["@bank", "@government"],
    header :contains "Subject" ["Urgent", "Dringend", "Belangrijk"]
) {
    addflag "\\Flagged";
}

# Newsletters - auto-read and move
if anyof (
    address :contains "From" "newsletter@",
    address :contains "From" "noreply@"
) {
    addflag "\\Seen";
    fileinto "Newsletter";
    stop;
}
```
