---
name: rlm
description: Use RLM (Recursive Language Models) for verified code execution, calculations, data analysis, and task decomposition. Executes Python code iteratively until producing verified results - no LLM guessing.
metadata: {"clawdbot":{"emoji":"🔄","requires":{"bins":["mcporter"]},"install":[{"id":"node","kind":"node","package":"mcporter","bins":["mcporter"],"label":"Install mcporter (npm)"}]}}
---

# RLM - Recursive Language Models

Execute tasks with **verified code execution** via mcporter MCP bridge.

RLM writes and executes Python code iteratively until it produces a verified answer. Unlike direct LLM responses, RLM computations are **100% accurate** for calculations.

## Available Tools

| Tool | Use For | Example |
|------|---------|---------|
| `rlm_execute` | General tasks, calculations | Calculate compound interest |
| `rlm_analyze` | Data analysis | Find patterns in dataset |
| `rlm_code` | Generate tested code | Write a sorting function |
| `rlm_decompose` | Complex multi-step tasks | Portfolio analysis |
| `rlm_status` | Check system status | Verify RLM is running |

## Quick Commands

**Simple calculation:**
```bash
mcporter call 'rlm.rlm_execute(task: "calculate 127 * 389")'
```

**First N primes:**
```bash
mcporter call 'rlm.rlm_execute(task: "calculate the first 100 prime numbers")'
```

**Data analysis:**
```bash
mcporter call 'rlm.rlm_analyze(data: "[23, 45, 67, 89, 12, 34]", question: "what is the mean, median, and standard deviation?")'
```

**Generate code:**
```bash
mcporter call 'rlm.rlm_code(description: "function to check if a number is prime")'
```

**Complex task (decomposed):**
```bash
mcporter call 'rlm.rlm_decompose(complex_task: "analyze a $500K portfolio with 60/30/10 allocation, calculate risk metrics and 10-year projection", num_subtasks: 5)'
```

**Check status:**
```bash
mcporter call 'rlm.rlm_status()'
```

## When to Use RLM

**Use RLM for:**
- Mathematical calculations requiring precision
- Statistical analysis (mean, std dev, correlations)
- Financial calculations (compound interest, NPV, IRR)
- Algorithm execution (primes, sorting, searching)
- Data transformations and aggregations
- Code generation with verification

**Don't use RLM for:**
- Simple factual questions (use direct response)
- Creative writing or brainstorming
- Tasks requiring web search or real-time data
- Very simple calculations (2+2)

## How It Works

```
1. You give RLM a task
2. RLM writes Python code to solve it
3. Code executes in sandbox
4. If not complete, RLM iterates
5. Returns verified final answer
```

**Models used:**
- Root: `grok-code-fast-1` (fast code execution)
- Subtasks: `gpt-4o-mini` (cheap sub-queries)

## Execution Logs

All RLM executions are logged to:
```
~/Claude/projects/rlm-original/logs/
```

Log format: `rlm_YYYY-MM-DD_HH-MM-SS_<id>.jsonl`

View logs in visualizer: `http://localhost:3000` (if running)

## Troubleshooting

**"Server offline" or "ModuleNotFoundError":**
```bash
# Check if mcporter can reach RLM
mcporter list | grep rlm

# Test RLM directly
mcporter call 'rlm.rlm_status()'
```

**Slow response:**
- RLM executes real code, typically 10-30 seconds
- Complex tasks with decomposition take longer
- Check logs for iteration count

**Wrong answer:**
- RLM code execution is deterministic
- Check if task description was clear
- Try rephrasing or decomposing the task

## Configuration

RLM MCP server config location: `~/.claude/mcp-servers/rlm/`

Environment variables:
- `RLM_MODEL` - Root model (default: grok-code-fast-1)
- `RLM_SUBTASK_MODEL` - Subtask model (default: gpt-4o-mini)
- `RLM_MAX_DEPTH` - Max recursion depth (default: 2)
- `RLM_MAX_ITERATIONS` - Max iterations (default: 20)

## References

- Paper: [Recursive Language Models](https://arxiv.org/abs/2512.24601) (Zhang, Kraska, Khattab 2025)
- Implementation: [github.com/alexzhang13/rlm](https://github.com/alexzhang13/rlm)
