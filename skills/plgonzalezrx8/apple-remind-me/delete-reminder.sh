#!/bin/bash
# Delete reminder(s) from Apple Reminders.app
# Usage: delete-reminder.sh ID [ID2 ID3...]

# Check if at least one ID provided
if [[ $# -eq 0 ]]; then
    echo "❌ Error: No reminder ID provided"
    echo "Usage: delete-reminder.sh ID [ID2 ID3...]"
    exit 1
fi

# Track success/failure
DELETED=()
FAILED=()

# Delete each reminder
for ID in "$@"; do
    OUTPUT=$(remindctl delete "$ID" --force 2>&1)
    if [[ $? -eq 0 ]]; then
        DELETED+=("$ID")
    else
        FAILED+=("$ID")
    fi
done

# Report results
if [[ ${#DELETED[@]} -gt 0 ]]; then
    echo "✅ Deleted reminder(s): ${DELETED[*]}"
fi

if [[ ${#FAILED[@]} -gt 0 ]]; then
    echo "❌ Failed to delete reminder(s): ${FAILED[*]}"
    exit 1
fi

if [[ ${#DELETED[@]} -gt 0 ]]; then
    echo "📱 Check Reminders.app to confirm removal"
fi
