#!/bin/bash
# Multi-LLM Intelligent Model Selection v1.1.0
# Trigger: multi llm
# Default: Always use Claude Opus 4.5

DEFAULT_MODEL="github-copilot/claude-opus-4.5"
TRIGGER_KEYWORD="multi llm"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

# Model definitions with fallback chains
declare -A PRIMARY_MODELS=(
    ["coding"]="qwen2.5-coder:32b"
    ["reasoning"]="deepseek-r1:70b"
    ["chinese"]="glm4:9b"
    ["general"]="qwen3:32b"
)

declare -A FALLBACK_MODELS=(
    ["coding"]="qwen2.5-coder:14b qwen3:32b"
    ["reasoning"]="deepseek-r1:32b qwen3:32b"
    ["chinese"]="qwen3:8b qwen3:32b"
    ["general"]="qwen3:14b qwen3:8b"
)

# Check if Ollama is running
check_ollama() {
    if curl -s --connect-timeout 2 http://localhost:11434/api/tags >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if a specific model is available
check_model_available() {
    local model="$1"
    if ! check_ollama; then
        return 1
    fi
    
    # Get list of available models and check exact match
    local available=$(curl -s http://localhost:11434/api/tags 2>/dev/null | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    
    if echo "$available" | grep -qx "$model"; then
        return 0
    fi
    
    # Also check partial match (model without tag)
    local base_model=$(echo "$model" | cut -d':' -f1)
    if echo "$available" | grep -q "^${base_model}:"; then
        return 0
    fi
    
    return 1
}

# Get available model with fallback chain
get_available_model() {
    local category="$1"
    local primary="${PRIMARY_MODELS[$category]}"
    local fallbacks="${FALLBACK_MODELS[$category]}"
    
    # Try primary model first
    if check_model_available "$primary"; then
        echo "$primary"
        return 0
    fi
    
    # Try fallback models
    for fallback in $fallbacks; do
        if check_model_available "$fallback"; then
            echo "$fallback"
            return 0
        fi
    done
    
    # Return primary anyway (caller should handle unavailability)
    echo "$primary"
    return 1
}

# Check if input contains trigger keyword
check_trigger() {
    local input="$1"
    if echo "$input" | grep -qi "multi llm"; then
        return 0  # Contains trigger
    else
        return 1  # No trigger
    fi
}

# Check for force model command
check_force_model() {
    local input="$1"
    
    if echo "$input" | grep -qi "multi llm coding"; then
        echo "coding"
        return 0
    fi
    
    if echo "$input" | grep -qi "multi llm reasoning"; then
        echo "reasoning"
        return 0
    fi
    
    if echo "$input" | grep -qi "multi llm chinese"; then
        echo "chinese"
        return 0
    fi
    
    if echo "$input" | grep -qi "multi llm general"; then
        echo "general"
        return 0
    fi
    
    return 1  # No force command
}

# Detect task category from input
detect_task_category() {
    local task="$1"
    
    # Remove trigger keyword for analysis
    task=$(echo "$task" | sed -E 's/multi llm (coding|reasoning|chinese|general)?//gi')
    
    # Detect coding task
    if echo "$task" | grep -qiE "代码|编程|函数|调试|debug|code|program|script|python|java|javascript|typescript|api|bug|重构|refactor|compile|syntax|class|method|variable"; then
        echo "coding"
        return
    fi
    
    # Detect reasoning task
    if echo "$task" | grep -qiE "推理|分析|证明|逻辑|数学|计算|reasoning|analysis|math|solve|算法|evaluate|proof|theorem|calculate|equation"; then
        echo "reasoning"
        return
    fi
    
    # Detect Chinese lightweight task
    if echo "$task" | grep -qiE "翻译|总结|摘要|简单|快速|translate|summary|brief"; then
        echo "chinese"
        return
    fi
    
    # Default to general
    echo "general"
}

# Main function
main() {
    local input="$1"
    local output_format="${2:-human}"  # human or json
    
    if [ -z "$input" ]; then
        echo "Usage: $0 \"your task\" [human|json]"
        echo ""
        echo "Default: Claude Opus 4.5"
        echo "Use 'multi llm' trigger to activate local model selection"
        echo ""
        echo "Examples:"
        echo "  $0 \"Help me write code\"                -> Claude Opus 4.5"
        echo "  $0 \"multi llm Help me write code\"      -> qwen2.5-coder:32b"
        echo "  $0 \"multi llm coding any task\"         -> qwen2.5-coder:32b"
        exit 1
    fi
    
    local selected_model=""
    local reason=""
    local category=""
    
    # Check if trigger is present
    if ! check_trigger "$input"; then
        # No trigger, use default model
        selected_model="$DEFAULT_MODEL"
        reason="Default model (no 'multi llm' trigger)"
        category="default"
    else
        # Trigger present, check for force command
        forced_category=$(check_force_model "$input")
        if [ -n "$forced_category" ]; then
            category="$forced_category"
            selected_model=$(get_available_model "$category")
            reason="Force command 'multi llm $category'"
        else
            # Intelligent detection
            category=$(detect_task_category "$input")
            selected_model=$(get_available_model "$category")
            reason="Detected $category task"
        fi
        
        # Check if model is actually available
        if ! check_model_available "$selected_model"; then
            reason="$reason (WARNING: model may not be available)"
        fi
    fi
    
    # Output
    if [ "$output_format" = "json" ]; then
        cat << EOF
{
  "model": "$selected_model",
  "category": "$category",
  "reason": "$reason",
  "trigger_found": $(check_trigger "$input" && echo "true" || echo "false"),
  "ollama_available": $(check_ollama && echo "true" || echo "false")
}
EOF
    else
        echo -e "${GREEN}Selected: $selected_model${NC}"
        echo -e "${CYAN}Reason: $reason${NC}"
        
        if [ "$category" != "default" ] && ! check_ollama; then
            echo -e "${RED}Warning: Ollama service not running${NC}"
        fi
    fi
}

main "$@"
