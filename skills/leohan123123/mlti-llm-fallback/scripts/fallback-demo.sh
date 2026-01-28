#!/bin/bash
# Multi-LLM Fallback Demo Script v1.1.0
# Demonstrates intelligent model selection with actual Ollama calls

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Model configuration
NETWORK_MODEL="github-copilot/claude-opus-4.5"

# Fallback chains
declare -A PRIMARY_MODELS=(
    ["coding"]="qwen2.5-coder:32b"
    ["reasoning"]="deepseek-r1:70b"
    ["chinese"]="glm4:9b"
    ["general"]="qwen3:32b"
)

declare -A FALLBACK_CHAINS=(
    ["coding"]="qwen2.5-coder:14b qwen2.5-coder:7b qwen3:32b"
    ["reasoning"]="deepseek-r1:32b deepseek-r1:14b qwen3:32b"
    ["chinese"]="qwen3:8b qwen3:4b qwen3:32b"
    ["general"]="qwen3:14b qwen3:8b qwen3:4b"
)

# Check Ollama service
check_ollama() {
    if curl -s --connect-timeout 3 http://localhost:11434/api/tags >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if specific model is available
check_model() {
    local model="$1"
    local available=$(curl -s http://localhost:11434/api/tags 2>/dev/null | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    echo "$available" | grep -q "$model"
}

# Get best available model in category
get_best_model() {
    local category="$1"
    local primary="${PRIMARY_MODELS[$category]}"
    local fallbacks="${FALLBACK_CHAINS[$category]}"
    
    if check_model "$primary"; then
        echo "$primary"
        return 0
    fi
    
    for model in $fallbacks; do
        if check_model "$model"; then
            echo "$model"
            return 0
        fi
    done
    
    echo "$primary"
    return 1
}

# Detect task category
detect_category() {
    local task="$1"
    task=$(echo "$task" | sed -E 's/multi llm (coding|reasoning|chinese|general)?//gi')
    
    if echo "$task" | grep -qiE "代码|编程|函数|调试|debug|code|program|script|python|java|javascript|api|bug|refactor"; then
        echo "coding"
    elif echo "$task" | grep -qiE "推理|分析|证明|逻辑|数学|计算|reasoning|analysis|math|solve|algorithm|proof"; then
        echo "reasoning"
    elif echo "$task" | grep -qiE "翻译|总结|摘要|简单|快速|translate|summary"; then
        echo "chinese"
    else
        echo "general"
    fi
}

# Call local model via Ollama
call_model() {
    local model="$1"
    local prompt="$2"
    
    echo -e "${CYAN}Calling: $model${NC}"
    echo -e "${YELLOW}Prompt: $prompt${NC}"
    echo ""
    
    response=$(echo "$prompt" | timeout 60 ollama run "$model" --nowordwrap 2>/dev/null | head -30)
    
    if [ -n "$response" ]; then
        echo -e "${GREEN}Response:${NC}"
        echo "$response"
        return 0
    else
        echo -e "${RED}No response from model${NC}"
        return 1
    fi
}

# Main demo function
demo() {
    local task="$1"
    local force_local="${2:-false}"
    
    echo ""
    echo -e "${BLUE}+----------------------------------------------------------+${NC}"
    echo -e "${BLUE}|         Multi-LLM Intelligent Switching Demo             |${NC}"
    echo -e "${BLUE}+----------------------------------------------------------+${NC}"
    echo ""
    
    # Step 1: Check Ollama
    echo -e "${CYAN}[1/4] Checking Ollama service...${NC}"
    if check_ollama; then
        echo -e "${GREEN}  Ollama running${NC}"
    else
        echo -e "${RED}  Ollama not running. Start with: ollama serve${NC}"
        exit 1
    fi
    
    # Step 2: Check trigger
    echo -e "${CYAN}[2/4] Checking for 'multi llm' trigger...${NC}"
    if echo "$task" | grep -qi "multi llm"; then
        echo -e "${GREEN}  Trigger found - activating local model selection${NC}"
    elif [ "$force_local" = "true" ]; then
        echo -e "${YELLOW}  No trigger, but --force-local specified${NC}"
    else
        echo -e "${GREEN}  No trigger - would use: $NETWORK_MODEL${NC}"
        echo -e "${YELLOW}  Use 'multi llm' prefix or --force-local to test local models${NC}"
        return 0
    fi
    
    # Step 3: Select model
    echo -e "${CYAN}[3/4] Selecting best model...${NC}"
    local category=$(detect_category "$task")
    local selected=$(get_best_model "$category")
    echo -e "${GREEN}  Category: $category${NC}"
    echo -e "${GREEN}  Selected: $selected${NC}"
    
    if ! check_model "$selected"; then
        echo -e "${YELLOW}  Warning: Model not available locally${NC}"
        echo -e "${YELLOW}  Pull with: ollama pull $selected${NC}"
        return 1
    fi
    
    # Step 4: Call model
    echo -e "${CYAN}[4/4] Calling model...${NC}"
    echo ""
    echo -e "${BLUE}----------------------------------------------------------${NC}"
    
    # Clean task (remove trigger)
    local clean_task=$(echo "$task" | sed -E 's/multi llm (coding|reasoning|chinese|general)?//gi' | xargs)
    call_model "$selected" "$clean_task"
    
    echo -e "${BLUE}----------------------------------------------------------${NC}"
    echo ""
    echo -e "${GREEN}Demo complete${NC}"
}

# Show help
show_help() {
    echo "Multi-LLM Demo - Test intelligent model switching"
    echo ""
    echo "Usage: $0 [OPTIONS] \"task description\""
    echo ""
    echo "Options:"
    echo "  --force-local, -f    Force local model (skip network model)"
    echo "  --list-models        List available Ollama models"
    echo "  --help, -h           Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 \"Help me write code\"                    # Uses Claude (no trigger)"
    echo "  $0 \"multi llm write a Python function\"    # Uses qwen2.5-coder"
    echo "  $0 --force-local \"explain recursion\"      # Force local model"
    echo ""
    echo "Task categories:"
    echo "  Coding    -> qwen2.5-coder:32b"
    echo "  Reasoning -> deepseek-r1:70b"
    echo "  Chinese   -> glm4:9b"
    echo "  General   -> qwen3:32b"
}

# List available models
list_models() {
    echo -e "${CYAN}Available Ollama models:${NC}"
    if check_ollama; then
        ollama list 2>/dev/null | tail -n +2
    else
        echo -e "${RED}Ollama not running${NC}"
    fi
}

# Entry point
main() {
    local force_local="false"
    local task=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force-local|-f)
                force_local="true"
                shift
                ;;
            --list-models)
                list_models
                exit 0
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                task="$1"
                shift
                ;;
        esac
    done
    
    if [ -z "$task" ]; then
        show_help
        exit 1
    fi
    
    demo "$task" "$force_local"
}

main "$@"
