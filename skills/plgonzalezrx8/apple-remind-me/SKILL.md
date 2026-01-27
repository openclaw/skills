---
name: apple-remind-me
description: Natural language reminders that create actual Apple Reminders.app entries (macOS-native)
metadata: {"clawdbot":{"emoji":"⏰","os":["darwin"],"requires":{"bins":["remindctl","date"]}}}
---

# Apple Remind Me (macOS Native)

Create, manage, and organize Apple Reminders using natural language. Works with Reminders.app natively - syncs to iPhone, iPad, Apple Watch.

## Quick Reference

| Want to... | Command | Example |
|-----------|---------|---------|
| Create reminder | `create-reminder.sh "msg" "when"` | `create-reminder.sh "Call mom" "tomorrow at 2pm"` |
| List reminders | `list-reminders.sh [filter]` | `list-reminders.sh today` |
| Complete reminder | `complete-reminder.sh ID` | `complete-reminder.sh XXXX-XXXX` |
| Delete reminder | `delete-reminder.sh ID` | `delete-reminder.sh XXXX-XXXX` |
| Edit message | `edit-reminder-message.sh ID "msg"` | `edit-reminder-message.sh XXXX "New text"` |
| Edit time | `edit-reminder-time.sh ID "when"` | `edit-reminder-time.sh XXXX "next friday"` |

## Available Commands

### 1. Create Reminder
Create a new reminder with natural language time parsing.

**Usage:**
```bash
./create-reminder.sh "message" "when"
```

**Examples:**
```bash
./create-reminder.sh "Pay bills" "later today"
./create-reminder.sh "Call dentist" "tomorrow at 3pm"
./create-reminder.sh "Check email" "in 2 hours"
./create-reminder.sh "Team meeting" "next monday at 10am"
```

### 2. List Reminders
Display all incomplete reminders with IDs, titles, due dates, and lists.

**Usage:**
```bash
./list-reminders.sh
```

**Output Format:**
```
⏳ ID: XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
   Title: Reminder text
   Due: 2026-01-27 14:00
   List: Reminders
```

### 3. Complete Reminder
Mark a reminder as completed (it will move to completed list in Reminders.app).

**Usage:**
```bash
./complete-reminder.sh "REMINDER-ID"
```

**Example:**
```bash
./complete-reminder.sh "CDCBCB94-1215-494E-9F12-471AFEF25C09"
```

### 4. Delete Reminder
Permanently delete a reminder.

**Usage:**
```bash
./delete-reminder.sh "REMINDER-ID"
```

**Example:**
```bash
./delete-reminder.sh "7C403BC5-6016-410A-810D-9A0F924682F9"
```

### 5. Edit Reminder Message
Update the text/title of an existing reminder.

**Usage:**
```bash
./edit-reminder-message.sh "REMINDER-ID" "new message"
```

**Example:**
```bash
./edit-reminder-message.sh "CDCBCB94-1215-494E-9F12-471AFEF25C09" "Updated reminder text"
```

### 6. Edit Reminder Time
Reschedule a reminder to a new time using natural language.

**Usage:**
```bash
./edit-reminder-time.sh "REMINDER-ID" "new time"
```

**Examples:**
```bash
./edit-reminder-time.sh "CDCBCB94-1215-494E-9F12-471AFEF25C09" "tomorrow at 2pm"
./edit-reminder-time.sh "CDCBCB94-1215-494E-9F12-471AFEF25C09" "in 3 hours"
./edit-reminder-time.sh "CDCBCB94-1215-494E-9F12-471AFEF25C09" "next friday"
```

## Time Parsing Reference

### Relative Times
Format: `in [number] [unit]`
- `in 5 minutes` → 5 minutes from now
- `in 2 hours` → 2 hours from now
- `in 3 days` → 3 days from now at current time

### Time of Day Shortcuts
- `later today` / `later` / `this afternoon` → Today at 17:00
- `tonight` → Today at 20:00
- `tomorrow` → Tomorrow at 09:00

### Tomorrow with Specific Time
Format: `tomorrow at [time]`
- `tomorrow at 3pm` → Tomorrow at 15:00
- `tomorrow at 10:30am` → Tomorrow at 10:30
- `tomorrow at 8pm` → Tomorrow at 20:00

### Day of Week
Format: `next [weekday]` (lowercase required)
- `next monday` → Next Monday at 09:00
- `next friday` → Next Friday at 09:00
- `next sunday` → Next Sunday at 09:00

**Note:** Day names must be lowercase (monday, tuesday, etc.)

### ISO Format (fallback)
- `2026-01-27 14:00` → Exact date and time

## Agent Implementation Guide

### Creating Reminders
When user says: "Remind me to X at/in Y"
```bash
./create-reminder.sh "X" "Y"
```

### Listing Reminders
When user asks: "What are my reminders?" or "Show my reminders"
```bash
./list-reminders.sh
```

### Completing Reminders
When user says: "Mark [reminder] as done" or "Complete [reminder]"
1. List reminders to find the ID
2. Use the ID to complete:
```bash
./complete-reminder.sh "REMINDER-ID"
```

### Editing Reminders
When user says: "Change [reminder] to say X" or "Reschedule [reminder] to Y"
1. List reminders to find the ID
2. Edit message or time:
```bash
./edit-reminder-message.sh "REMINDER-ID" "new message"
./edit-reminder-time.sh "REMINDER-ID" "new time"
```

### Deleting Reminders
When user says: "Delete [reminder]" or "Remove [reminder]"
1. List reminders to find the ID
2. Delete:
```bash
./delete-reminder.sh "REMINDER-ID"
```

## Workflow Examples

### Complete Workflow: Find and Complete a Reminder
```bash
# 1. List all reminders
./list-reminders.sh | grep "Pay bills"

# 2. Get the ID from output
# Output shows: ID: CDCBCB94-1215-494E-9F12-471AFEF25C09

# 3. Mark as complete
./complete-reminder.sh "CDCBCB94-1215-494E-9F12-471AFEF25C09"
```

### Complete Workflow: Reschedule a Reminder
```bash
# 1. List reminders and find the one to reschedule
./list-reminders.sh | grep "Team meeting"

# 2. Reschedule to new time
./edit-reminder-time.sh "REMINDER-ID" "next friday at 2pm"
```

## Technical Details

- **Backend:** Uses `remindctl` command-line tool (macOS native)
- **Date Parsing:** BSD date utility (macOS compatible)
- **Time Format:** ISO 8601 timestamps for remindctl
- **List Filtering:** Shows only incomplete reminders by default
- **Sync:** All changes sync immediately to iCloud and all devices

## Requirements

- macOS (darwin)
- `remindctl` (installed at `/usr/local/bin/remindctl`)
- `date` (BSD version, macOS default)
- `python3` (for JSON parsing in list-reminders.sh)
- Apple Reminders.app

## Limitations

- Day of week parsing requires lowercase (e.g., "monday" not "Monday")
- "Next [weekday]" adds 7 days (doesn't calculate exact next occurrence)
- No support for recurring reminders
- No support for custom reminder lists (uses default "Reminders" list)
- No location-based reminders
