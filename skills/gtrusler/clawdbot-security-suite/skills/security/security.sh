#!/bin/bash
# Clawdbot Security Suite - Main CLI
# Usage: security <command> [options]

set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SKILL_DIR/config.json"
PATTERNS_FILE="$SKILL_DIR/patterns.json"
LOG_FILE="$HOME/.clawdbot/logs/security-events.log"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log_event() {
    local level="$1"
    local message="$2"
    local timestamp=$(date -Iseconds)
    echo "${timestamp} [${level}] ${message}" >> "$LOG_FILE"
    
    case "$level" in
        "THREAT")
            echo -e "${RED}❌ THREAT DETECTED:${NC} $message"
            ;;
        "SAFE")
            echo -e "${GREEN}✅ SAFE:${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠️ WARNING:${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ️ INFO:${NC} $message"
            ;;
    esac
}

# Load patterns from JSON file
load_patterns() {
    if [[ ! -f "$PATTERNS_FILE" ]]; then
        log_event "ERROR" "Patterns file not found: $PATTERNS_FILE"
        exit 1
    fi
    cat "$PATTERNS_FILE"
}

# Validate command for injection attempts
validate_command() {
    local command="$1"
    local patterns=$(load_patterns | jq -r '.command_injection[]')
    
    while IFS= read -r pattern; do
        if [[ "$command" =~ $pattern ]]; then
            log_event "THREAT" "Command injection - Pattern: $pattern - Command: $command"
            echo "BLOCKED"
            return 1
        fi
    done <<< "$patterns"
    
    log_event "SAFE" "Command validated - $command"
    echo "ALLOWED"
    return 0
}

# Check URL for SSRF and malicious patterns
check_url() {
    local url="$1"
    local patterns=$(load_patterns | jq -r '.ssrf[]')
    
    while IFS= read -r pattern; do
        if [[ "$url" =~ $pattern ]]; then
            log_event "THREAT" "SSRF attempt - Pattern: $pattern - URL: $url"
            echo "BLOCKED"
            return 1
        fi
    done <<< "$patterns"
    
    log_event "SAFE" "URL validated - $url"
    echo "ALLOWED"
    return 0
}

# Scan content for multiple threat types
scan_content() {
    local content="$1"
    
    # Check prompt injection patterns
    local prompt_patterns=$(load_patterns | jq -r '.prompt_injection[]')
    while IFS= read -r pattern; do
        if [[ "$content" =~ $pattern ]]; then
            log_event "THREAT" "Prompt injection - Pattern: $pattern"
            echo "FLAGGED"
            return 1
        fi
    done <<< "$prompt_patterns"
    
    # Check API key patterns
    local api_patterns=$(load_patterns | jq -r '.api_keys[]')
    while IFS= read -r pattern; do
        if [[ "$content" =~ $pattern ]]; then
            log_event "THREAT" "API key exposure - Pattern: $pattern"
            echo "FLAGGED"
            return 1
        fi
    done <<< "$api_patterns"
    
    log_event "SAFE" "Content scanned - clean"
    echo "CLEAN"
    return 0
}

# Validate file path
validate_path() {
    local path="$1"
    local patterns=$(load_patterns | jq -r '.path_traversal[]')
    
    while IFS= read -r pattern; do
        if [[ "$path" =~ $pattern ]]; then
            log_event "THREAT" "Path traversal - Pattern: $pattern - Path: $path"
            echo "BLOCKED"
            return 1
        fi
    done <<< "$patterns"
    
    # Check for sensitive system files
    local sensitive_patterns=$(load_patterns | jq -r '.sensitive_files[]')
    while IFS= read -r pattern; do
        if [[ "$path" =~ $pattern ]]; then
            log_event "WARNING" "Sensitive file access - Path: $path"
            echo "SENSITIVE"
            return 2
        fi
    done <<< "$sensitive_patterns"
    
    log_event "SAFE" "Path validated - $path"
    echo "ALLOWED"
    return 0
}

# Show recent security events
show_events() {
    local timespan="${1:-24h}"
    local hours
    
    case "$timespan" in
        *h) hours="${timespan%h}" ;;
        *d) hours=$((${timespan%d} * 24)) ;;
        *) hours=24 ;;
    esac
    
    if [[ ! -f "$LOG_FILE" ]]; then
        log_event "INFO" "No security events logged yet"
        return 0
    fi
    
    local cutoff=$(date -d "$hours hours ago" -Iseconds 2>/dev/null || date -v-${hours}H -Iseconds)
    
    echo -e "${BLUE}Security Events (Last $timespan):${NC}"
    echo "================================"
    
    awk -v cutoff="$cutoff" '$1 >= cutoff' "$LOG_FILE" | tail -50 | while read -r line; do
        if [[ "$line" =~ THREAT ]]; then
            echo -e "${RED}$line${NC}"
        elif [[ "$line" =~ SAFE ]]; then
            echo -e "${GREEN}$line${NC}"
        elif [[ "$line" =~ WARNING ]]; then
            echo -e "${YELLOW}$line${NC}"
        else
            echo "$line"
        fi
    done
}

# Show security statistics
show_stats() {
    if [[ ! -f "$LOG_FILE" ]]; then
        echo "No security events recorded"
        return 0
    fi
    
    local total=$(wc -l < "$LOG_FILE")
    local threats=$(grep -c "THREAT" "$LOG_FILE" || echo "0")
    local safe=$(grep -c "SAFE" "$LOG_FILE" || echo "0")
    local warnings=$(grep -c "WARNING" "$LOG_FILE" || echo "0")
    
    echo -e "${BLUE}Security Statistics:${NC}"
    echo "=================="
    echo "Total Events: $total"
    echo -e "Threats Blocked: ${RED}$threats${NC}"
    echo -e "Safe Operations: ${GREEN}$safe${NC}"
    echo -e "Warnings: ${YELLOW}$warnings${NC}"
    
    if [[ $threats -gt 0 ]]; then
        echo ""
        echo -e "${YELLOW}Recent Threat Types:${NC}"
        grep "THREAT" "$LOG_FILE" | tail -10 | cut -d']' -f2- | sort | uniq -c | sort -nr
    fi
}

# Main command dispatcher
case "${1:-help}" in
    "validate-command")
        [[ $# -eq 2 ]] || { echo "Usage: security validate-command <command>"; exit 1; }
        validate_command "$2"
        ;;
    "check-url")
        [[ $# -eq 2 ]] || { echo "Usage: security check-url <url>"; exit 1; }
        check_url "$2"
        ;;
    "scan-content")
        [[ $# -eq 2 ]] || { echo "Usage: security scan-content <text>"; exit 1; }
        scan_content "$2"
        ;;
    "validate-path")
        [[ $# -eq 2 ]] || { echo "Usage: security validate-path <path>"; exit 1; }
        validate_path "$2"
        ;;
    "events")
        show_events "${2:-24h}"
        ;;
    "stats")
        show_stats
        ;;
    "config")
        cat "$CONFIG_FILE" 2>/dev/null || echo "Config file not found"
        ;;
    "patterns")
        jq '.' "$PATTERNS_FILE" 2>/dev/null || echo "Patterns file not found"
        ;;
    "help"|*)
        echo "Clawdbot Security Suite"
        echo "======================"
        echo ""
        echo "Commands:"
        echo "  validate-command <cmd>  - Validate bash command safety"
        echo "  check-url <url>        - Check URL for SSRF/threats"
        echo "  scan-content <text>    - Scan for injection patterns"
        echo "  validate-path <path>   - Check file path safety"
        echo "  events [timespan]      - Show security events (24h, 7d, etc)"
        echo "  stats                  - Show security statistics"
        echo "  config                 - Show configuration"
        echo "  patterns               - Show detection patterns"
        echo "  help                   - Show this help"
        ;;
esac