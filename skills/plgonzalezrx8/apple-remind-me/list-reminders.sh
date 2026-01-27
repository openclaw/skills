#!/bin/bash
# List reminders from Apple Reminders.app
# Usage: list-reminders.sh [filter]
# Filters: all (default), today, tomorrow, week, overdue, completed

FILTER="${1:-all}"

# Validate filter
case "$FILTER" in
    all|today|tomorrow|week|overdue|completed)
        ;;
    *)
        echo "❌ Error: Invalid filter '$FILTER'"
        echo "Valid filters: all, today, tomorrow, week, overdue, completed"
        exit 1
        ;;
esac

# Get reminders as JSON
OUTPUT=$(remindctl show "$FILTER" --json 2>&1)

if [[ $? -ne 0 ]]; then
    echo "❌ Error fetching reminders: $OUTPUT"
    exit 1
fi

# Parse and display using Python
python3 - "$OUTPUT" <<'PYTHON'
import sys
import json
from datetime import datetime

try:
    data = json.loads(sys.argv[1])
except json.JSONDecodeError as e:
    print(f"❌ Error parsing reminders: {e}")
    sys.exit(1)

# Handle empty results
if not data:
    print("📭 No reminders found")
    sys.exit(0)

# Print header
print("📝 Reminders:\n")

# Format and display each reminder
for reminder in data:
    reminder_id = reminder.get('id', 'N/A')
    title = reminder.get('title', 'Untitled')
    completed = reminder.get('completed', False)
    due_date = reminder.get('dueDate')
    list_name = reminder.get('list', 'Reminders')

    # Status emoji
    status = "✅" if completed else "⏳"

    # Format due date
    if due_date:
        try:
            dt = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            due_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            due_str = due_date
    else:
        due_str = "No due date"

    # Print reminder
    print(f"{status} ID: {reminder_id}")
    print(f"   Title: {title}")
    print(f"   Due: {due_str}")
    print(f"   List: {list_name}")
    print()

PYTHON
