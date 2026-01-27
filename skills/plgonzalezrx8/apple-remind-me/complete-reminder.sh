#!/bin/bash
# Mark reminder(s) as completed in Apple Reminders.app
# Usage: complete-reminder.sh ID [ID2 ID3...]

# Check if at least one ID provided
if [[ $# -eq 0 ]]; then
    echo "❌ Error: No reminder ID provided"
    echo "Usage: complete-reminder.sh ID [ID2 ID3...]"
    exit 1
fi

# Complete the reminder(s) - remindctl accepts multiple IDs
OUTPUT=$(remindctl complete "$@" 2>&1)

if [[ $? -eq 0 ]]; then
    if [[ $# -eq 1 ]]; then
        echo "✅ Reminder $1 marked as completed"
    else
        echo "✅ Reminders $@ marked as completed"
    fi
    echo "📱 Check Reminders.app to see the change"
else
    echo "❌ Error completing reminder(s): $OUTPUT"
    exit 1
fi
