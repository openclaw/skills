---
name: accli
description: This skill should be used when interacting with Apple Calendar on macOS. Use it for listing calendars, viewing events, creating/updating/deleting calendar events, and checking availability/free-busy times. Triggers on requests like "check my calendar", "schedule a meeting", "what's on my schedule", "am I free tomorrow", or any calendar-related operations.
---

# Apple Calendar CLI (accli)

## Installation

```bash
npm install -g @joargp/accli
```

**Requirements:** macOS only (uses JavaScript for Automation)

## Overview

The accli tool provides command-line access to macOS Apple Calendar. It enables listing calendars, querying events, creating/updating/deleting events, and checking availability across calendars.

## Quick Reference

### DateTime Formats
- Timed events: YYYY-MM-DDTHH:mm or YYYY-MM-DDTHH:mm:ss
- All-day events: YYYY-MM-DD

### Global Options
- --json - Output as JSON (recommended for parsing)
- --help - Show help for any command

## Commands

### List Calendars

```
accli calendars [--json]
```

Lists all available calendars with names and persistent IDs. Run this first to discover available calendars and their IDs.

### List Events

```
accli events <calendarName> [options]
```

Options:
- --calendar-id <id> - Persistent calendar ID (recommended over name)
- --from <datetime> - Start of range (default: now)
- --to <datetime> - End of range (default: from + 7 days)
- --max <n> - Maximum events to return (default: 50)
- --query <q> - Case-insensitive filter on summary/location/description
- --json - Output JSON

Examples:

```bash
# Events from Work calendar for this week
accli events Work --json

# Events in January
accli events Work --from 2025-01-01 --to 2025-01-31 --json

# Search for specific events
accli events Work --query "standup" --max 10 --json
```

### Get Single Event

```
accli event <calendarName> <eventId> [--json]
```

Retrieves details for a specific event by its ID.

### Create Event

```
accli create <calendarName> --summary <s> --start <datetime> --end <datetime> [options]
```

Required Options:
- --summary <s> - Event title
- --start <datetime> - Start time
- --end <datetime> - End time

Optional:
- --location <l> - Event location
- --description <d> - Event description
- --all-day - Create an all-day event
- --json - Output JSON

Examples:

```bash
# Create a timed meeting
accli create Work --summary "Team Standup" --start 2025-01-15T09:00 --end 2025-01-15T09:30 --json

# Create an all-day event
accli create Personal --summary "Vacation" --start 2025-07-01 --end 2025-07-05 --all-day --json

# Create with location and description
accli create Work --summary "Client Meeting" --start 2025-01-15T14:00 --end 2025-01-15T15:00 \
  --location "Conference Room A" --description "Q1 planning discussion" --json
```

### Update Event

```
accli update <calendarName> <eventId> [options]
```

Options (all optional - only provide what to change):
- --summary <s> - New title
- --start <datetime> - New start time
- --end <datetime> - New end time
- --location <l> - New location
- --description <d> - New description
- --all-day - Convert to all-day event
- --no-all-day - Convert to timed event
- --json - Output JSON

Example:

```bash
accli update Work event-id-123 --summary "Updated Meeting Title" --start 2025-01-15T15:00 --end 2025-01-15T16:00 --json
```

### Delete Event

```
accli delete <calendarName> <eventId> [--json]
```

Permanently deletes an event. Confirm with user before executing.

### Check Free/Busy

```
accli freebusy --calendar <name> --from <datetime> --to <datetime> [options]
```

Options:
- --calendar <name> - Calendar name (can repeat for multiple calendars)
- --calendar-id <id> - Persistent calendar ID (can repeat)
- --from <datetime> - Start of range (required)
- --to <datetime> - End of range (required)
- --json - Output JSON

Shows busy time slots, excluding cancelled, declined, and transparent events.

Examples:

```bash
# Check availability across calendars
accli freebusy --calendar Work --calendar Personal --from 2025-01-15 --to 2025-01-16 --json

# Check specific hours
accli freebusy --calendar Work --from 2025-01-15T09:00 --to 2025-01-15T18:00 --json
```

### Configuration

```bash
# Set default calendar (interactive)
accli config set-default

# Set default by name
accli config set-default --calendar Work

# Show current config
accli config show

# Clear default
accli config clear
```

When a default calendar is set, commands automatically use it if no calendar is specified.

## Workflow Guidelines

### Before Creating Events
1. List calendars to get available calendar names/IDs
2. Check free/busy to find available time slots
3. Confirm event details with user before creating

### Best Practices
- Always use --json flag for programmatic parsing
- Prefer --calendar-id over calendar names for reliability
- When querying events, start with reasonable date ranges
- Confirm with user before delete operations
- Use ISO 8601 datetime format consistently

### Common Patterns

Find a free slot and schedule:

```bash
# 1. Check availability
accli freebusy --calendar Work --from 2025-01-15T09:00 --to 2025-01-15T18:00 --json

# 2. Create event in available slot
accli create Work --summary "Meeting" --start 2025-01-15T14:00 --end 2025-01-15T15:00 --json
```

View today's schedule:

```bash
accli events Work --from $(date +%Y-%m-%d) --to $(date -v+1d +%Y-%m-%d) --json
```
