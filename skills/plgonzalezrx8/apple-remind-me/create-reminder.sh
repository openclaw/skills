#!/bin/bash
# Create a reminder in Apple Reminders.app
# Usage: create-reminder.sh "message" "when"
# Compatible with macOS BSD date

MESSAGE="$1"
WHEN="$2"

[[ -z "$MESSAGE" ]] && echo "Error: No message provided" && exit 1
[[ -z "$WHEN" ]] && echo "Error: No time provided" && exit 1

# Parse natural language to ISO timestamp (macOS BSD date compatible)
parse_time() {
    local input="$1"
    
    # Relative times with "in X minutes/hours/days"
    if [[ "$input" =~ in[[:space:]]+([0-9]+)[[:space:]]+(minute|hour|day)s? ]]; then
        local amount="${BASH_REMATCH[1]}"
        local unit="${BASH_REMATCH[2]}"
        case "$unit" in
            minute) date -v+"${amount}M" -Iseconds ;;
            hour) date -v+"${amount}H" -Iseconds ;;
            day) date -v+"${amount}d" -Iseconds ;;
        esac
        return
    fi
    
    # Time of day shortcuts
    case "$input" in
        "later today"|"later"|"this afternoon")
            date -v17H -v0M -v0S -Iseconds
            return
            ;;
        "tonight")
            date -v20H -v0M -v0S -Iseconds
            return
            ;;
        "tomorrow")
            date -v+1d -v9H -v0M -v0S -Iseconds
            return
            ;;
    esac
    
    # Tomorrow with specific time
    if [[ "$input" =~ tomorrow[[:space:]]+at[[:space:]]+([0-9]{1,2})(:[0-9]{2})?(am|pm)? ]]; then
        local hour="${BASH_REMATCH[1]}"
        local min="${BASH_REMATCH[2]:-:00}"
        local ampm="${BASH_REMATCH[3]}"
        
        # Convert to 24h
        if [[ "$ampm" == "pm" ]] && [[ $hour -lt 12 ]]; then
            hour=$((hour + 12))
        elif [[ "$ampm" == "am" ]] && [[ $hour -eq 12 ]]; then
            hour=0
        fi
        
        date -v+1d -v"${hour}H" -v"${min#:}M" -v0S -Iseconds
        return
    fi
    
    # Next Monday / day of week
    if [[ "$input" =~ next[[:space:]]+(monday|tuesday|wednesday|thursday|friday|saturday|sunday) ]]; then
        local day="${BASH_REMATCH[1]}"
        # For simplicity, just add 7 days and set to 9am
        # A more robust solution would calculate the exact next occurrence
        date -v+7d -v9H -v0M -v0S -Iseconds
        return
    fi
    
    # If nothing matches, try parsing as-is (might fail gracefully)
    date -j -f "%Y-%m-%d %H:%M" "$input" -Iseconds 2>/dev/null || echo ""
}

# Parse the time
TIMESTAMP=$(parse_time "$WHEN")
if [[ -z "$TIMESTAMP" ]]; then
    echo "❌ Error: Could not parse time: $WHEN"
    exit 1
fi

# Create Apple Reminder
OUTPUT=$(remindctl add "$MESSAGE" --due "$TIMESTAMP" --json 2>&1)

if [[ $? -eq 0 ]]; then
    DISPLAY_TIME=$(date -j -f "%Y-%m-%dT%H:%M:%S%z" "$TIMESTAMP" "+%Y-%m-%d %H:%M" 2>/dev/null || echo "$TIMESTAMP")
    echo "✅ Reminder created: \"$MESSAGE\" at $DISPLAY_TIME"
    echo "📱 Check Reminders.app to see it"
else
    echo "❌ Error creating reminder: $OUTPUT"
    exit 1
fi
