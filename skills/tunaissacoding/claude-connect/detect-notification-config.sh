#!/bin/bash
# detect-notification-config.sh - Auto-detect notification settings from Clawdbot config
# Follows target formats from Clawdbot docs: https://docs.clawd.bot/channels/

set -euo pipefail

CLAWDBOT_CONFIG="$HOME/.clawdbot/clawdbot.json"
SESSIONS_FILE="$HOME/.clawdbot/agents/main/sessions/sessions.json"

# Output format: channel|target
# Target formats (per Clawdbot docs https://docs.clawd.bot/channels/):
#   telegram: numeric ID (123456789) or @username
#   discord:  user:<id> for DMs, channel:<channelId> for guild channels
#   slack:    user:<id> for DMs, channel:<id> for channels
#   signal:   E.164 phone (+15551234567), signal:group:<groupId>, or username:<name>
#   whatsapp: E.164 phone number (+15551234567)

detect_notification_target() {
    if ! command -v jq &> /dev/null; then
        return 1
    fi
    
    if [[ ! -f "$SESSIONS_FILE" ]]; then
        return 1
    fi
    
    # Find first direct (non-group) session with delivery context
    local session_data=$(jq -r '
        to_entries[] | 
        select(.value.chatType == "direct") |
        select(.value.deliveryContext != null) |
        {
            channel: .value.deliveryContext.channel,
            to: (.value.deliveryContext.to // .value.lastTo)
        } | 
        @json
    ' "$SESSIONS_FILE" 2>/dev/null | head -1)
    
    if [[ -z "$session_data" ]]; then
        return 1
    fi
    
    local channel=$(echo "$session_data" | jq -r '.channel')
    local raw_target=$(echo "$session_data" | jq -r '.to')
    
    if [[ -z "$channel" ]] || [[ -z "$raw_target" ]]; then
        return 1
    fi
    
    # Format target according to channel docs
    local target=""
    case "$channel" in
        telegram)
            # Telegram: just numeric ID or @username
            # Session format: "telegram:123456789" → extract "123456789"
            target="${raw_target#telegram:}"
            ;;
        discord)
            # Discord: user:<id> for DMs
            # Session format: "discord:user:123456789" or similar
            local id="${raw_target#discord:}"
            if [[ "$id" != user:* ]]; then
                target="user:${id}"
            else
                target="$id"
            fi
            ;;
        slack)
            # Slack: user:<id> for DMs
            # Session format: "slack:user:U123456789" or similar
            local id="${raw_target#slack:}"
            if [[ "$id" != user:* ]]; then
                target="user:${id}"
            else
                target="$id"
            fi
            ;;
        signal)
            # Signal: signal:+15551234567 or plain E.164, signal:group:<groupId>, username:<name>
            # Session format: "signal:+15551234567" → keep as-is or use plain E.164
            local id="${raw_target#signal:}"
            # If it's a phone number (starts with +), use plain E.164
            if [[ "$id" == +* ]]; then
                target="$id"
            else
                # Keep other formats (group:, username:, etc.)
                target="$id"
            fi
            ;;
        whatsapp)
            # WhatsApp: phone number
            target="${raw_target#whatsapp:}"
            ;;
        *)
            # Unknown channel: try stripping channel prefix
            target="${raw_target#${channel}:}"
            ;;
    esac
    
    if [[ -n "$target" ]]; then
        echo "${channel}|${target}"
        return 0
    fi
    
    return 1
}

# Main
main() {
    if result=$(detect_notification_target); then
        echo "$result"
        exit 0
    fi
    exit 1
}

main
