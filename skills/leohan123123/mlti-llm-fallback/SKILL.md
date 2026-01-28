---
name: multi-llm
description: Multi-LLM intelligent switching. Use command 'multi llm' to activate local model selection based on task type. Default uses Claude Opus 4.5.
trigger: multi llm
version: 1.1.0
author: leohan123123
tags: llm, ollama, local-model, fallback, multi-model
---

# Multi-LLM - Intelligent Model Switching

**Trigger Command**: `multi llm`

> **Default Behavior**: Always use Claude Opus 4.5 (strongest model)
> Only when the message contains `multi llm` command will local model selection be activated.

## What's New in v1.1.0

- Renamed trigger from `mlti llm` to `multi llm` (clearer naming)
- Enhanced model existence checking with fallback chain
- Added detailed usage examples and troubleshooting
- Improved task detection patterns

## Usage

### Default Mode (without command)
```
Help me write a Python function -> Uses Claude Opus 4.5
Analyze this code -> Uses Claude Opus 4.5
```

### Multi-Model Mode (with command)
```
multi llm Help me write a Python function -> Selects qwen2.5-coder:32b
multi llm Analyze this math proof -> Selects deepseek-r1:70b
multi llm Translate to Chinese -> Selects glm4:9b
```

## Command Format

| Command | Description |
|---------|-------------|
| `multi llm` | Activate intelligent model selection |
| `multi llm coding` | Force coding model |
| `multi llm reasoning` | Force reasoning model |
| `multi llm chinese` | Force Chinese model |
| `multi llm general` | Force general model |

## Model Mapping

**Primary Model (Default)**: github-copilot/claude-opus-4.5

**Local Models (when `multi llm` triggered)**:

| Task Type | Model | Size | Best For |
|-----------|-------|------|----------|
| Coding | qwen2.5-coder:32b | 19GB | Code generation, debugging, refactoring |
| Reasoning | deepseek-r1:70b | 42GB | Math, logic, complex analysis |
| Chinese | glm4:9b | 5.5GB | Translation, summaries, quick tasks |
| General | qwen3:32b | 20GB | General purpose, fallback |

### Fallback Chain

If the selected model is unavailable, the system tries alternatives:

```
Coding:    qwen2.5-coder:32b -> qwen2.5-coder:14b -> qwen3:32b
Reasoning: deepseek-r1:70b -> deepseek-r1:32b -> qwen3:32b
Chinese:   glm4:9b -> qwen3:8b -> qwen3:32b
General:   qwen3:32b -> qwen3:14b -> qwen3:8b
```

## Detection Logic

```
User Input
    |
    v
Contains "multi llm"?
    |
    +-- No -> Use Claude Opus 4.5 (default)
    |
    +-- Yes -> Task Type Detection
                |
        +-------+-------+-------+
        v       v       v       v
      Coding  Reasoning Chinese General
        |       |       |       |
        v       v       v       v
    qwen2.5  deepseek  glm4   qwen3
    coder    r1:70b    :9b    :32b
```

### Task Detection Keywords

| Category | Keywords (EN) | Keywords (CN) |
|----------|---------------|---------------|
| Coding | code, debug, function, script, api, bug, refactor, python, java, javascript | 代码, 编程, 函数, 调试, 重构 |
| Reasoning | analysis, proof, logic, math, solve, algorithm, evaluate | 推理, 分析, 证明, 逻辑, 数学, 计算, 算法 |
| Chinese | translate, summary | 翻译, 总结, 摘要, 简单, 快速 |

## Examples

### Example 1: Coding Task
```bash
# Input
multi llm Write a Python function to calculate fibonacci

# Output
Selected: qwen2.5-coder:32b
Reason: Detected coding task (keywords: python, function)
```

### Example 2: Math Analysis
```bash
# Input
multi llm reasoning Prove that sqrt(2) is irrational

# Output
Selected: deepseek-r1:70b
Reason: Force command 'reasoning' used
```

### Example 3: Quick Translation
```bash
# Input
multi llm 把这段话翻译成英文

# Output
Selected: glm4:9b
Reason: Detected Chinese lightweight task (keywords: 翻译)
```

### Example 4: Default (No trigger)
```bash
# Input
Write a REST API with authentication

# Output
Selected: claude-opus-4.5
Reason: Default model (no 'multi llm' trigger)
```

## Prerequisites

1. **Ollama** must be installed and running:
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve

# Pull required models
ollama pull qwen2.5-coder:32b
ollama pull deepseek-r1:70b
ollama pull glm4:9b
ollama pull qwen3:32b
```

2. **Check available models**:
```bash
ollama list
```

## Troubleshooting

### Model not found
```bash
# Check if model exists
ollama list | grep "qwen2.5-coder"

# Pull missing model
ollama pull qwen2.5-coder:32b
```

### Ollama not running
```bash
# Check service status
curl -s http://localhost:11434/api/tags

# Start Ollama
ollama serve &
```

### Slow response
- Large models (70b) require significant RAM/VRAM
- Consider using smaller variants: `deepseek-r1:32b` instead of `70b`

### Wrong model selected
- Use force commands: `multi llm coding`, `multi llm reasoning`
- Check if keywords match your task type

## Files in This Skill

```
multi-llm/
├── SKILL.md              # This documentation
└── scripts/
    ├── select-model.sh   # Model selection logic
    └── fallback-demo.sh  # Interactive demo script
```

## Integration

### With OpenCode/ClaudeCode

The trigger `multi llm` is detected in your message. Simply prefix your request:

```
multi llm [your request here]
```

### Programmatic Usage

```bash
# Get recommended model for a task
./scripts/select-model.sh "multi llm write a sorting algorithm"
# Output: qwen2.5-coder:32b

# Demo with actual model call
./scripts/fallback-demo.sh --force-local "explain recursion"
```

## Author

- GitHub: [@leohan123123](https://github.com/leohan123123)

## License

MIT
