---
name: featurebase
description: Featurebase API for customer feedback, feature requests, changelogs, and support. Use for managing user feedback, tracking feature votes, responding to support requests, or publishing changelog updates.
---

# Featurebase

Customer feedback platform API for feature requests, support, and changelogs.

## Setup

Get your API key from Featurebase:
1. Go to Settings → API
2. Copy your API key

Store in `~/.clawdbot/clawdbot.json`:
```json
{
  "skills": {
    "entries": {
      "featurebase": {
        "apiKey": "YOUR_API_KEY",
        "orgSubdomain": "whisperit"
      }
    }
  }
}
```

Or set env: `FEATUREBASE_API_KEY=xxx` and `FEATUREBASE_ORG=whisperit`

## Quick Reference

### Posts (Feature Requests & Feedback)
```bash
{baseDir}/scripts/featurebase.sh posts list                     # List all posts
{baseDir}/scripts/featurebase.sh posts list --status open       # Filter by status
{baseDir}/scripts/featurebase.sh posts list --board feedback    # Filter by board
{baseDir}/scripts/featurebase.sh posts show <id>                # Get post details
{baseDir}/scripts/featurebase.sh posts create --title "Title" --content "Description" --board feedback
{baseDir}/scripts/featurebase.sh posts update <id> --status "in-progress"
{baseDir}/scripts/featurebase.sh posts comment <id> --content "Reply text"
```

### Support / Help Desk
```bash
{baseDir}/scripts/featurebase.sh support list                   # List support tickets
{baseDir}/scripts/featurebase.sh support list --status open     # Open tickets only
{baseDir}/scripts/featurebase.sh support show <id>              # Ticket details
{baseDir}/scripts/featurebase.sh support reply <id> --content "Response"
{baseDir}/scripts/featurebase.sh support close <id>             # Close ticket
```

### Changelog
```bash
{baseDir}/scripts/featurebase.sh changelog list                 # List entries
{baseDir}/scripts/featurebase.sh changelog create --title "v2.0" --content "Release notes..."
{baseDir}/scripts/featurebase.sh changelog publish <id>         # Publish draft
```

### Users
```bash
{baseDir}/scripts/featurebase.sh users list                     # List users
{baseDir}/scripts/featurebase.sh users search "email@example.com"
{baseDir}/scripts/featurebase.sh users show <id>                # User details + activity
```

### Boards
```bash
{baseDir}/scripts/featurebase.sh boards list                    # List all boards
```

## Post Statuses
- `open` - New/open for voting
- `under-review` - Being reviewed
- `planned` - Scheduled for development
- `in-progress` - Currently being worked on
- `complete` - Done
- `closed` - Won't do / closed

## Common Workflows

### Respond to Top Feature Request
```bash
# Find top-voted open requests
{baseDir}/scripts/featurebase.sh posts list --status open --sort votes

# Add a status update
{baseDir}/scripts/featurebase.sh posts update <id> --status planned
{baseDir}/scripts/featurebase.sh posts comment <id> --content "We're planning this for Q1!"
```

### Handle Support Queue
```bash
# List open tickets
{baseDir}/scripts/featurebase.sh support list --status open

# Reply to a ticket
{baseDir}/scripts/featurebase.sh support reply <id> --content "Thanks for reaching out..."

# Close resolved tickets
{baseDir}/scripts/featurebase.sh support close <id>
```

## Notes

- API Base: `https://do.featurebase.app/v2`
- Auth: Bearer token via `Authorization` header
- Org subdomain: Your Featurebase subdomain (e.g., `whisperit.featurebase.app`)
- Rate limits: Refer to Featurebase docs for current limits
- Always confirm before modifying or closing tickets
