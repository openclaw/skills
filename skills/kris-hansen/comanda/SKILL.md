---
name: comanda
description: Generate, visualize, and execute declarative AI pipelines using the comanda CLI. Use when creating LLM workflows from natural language, viewing workflow charts, editing YAML workflow files, or processing/running comanda workflows. Supports multi-model orchestration (OpenAI, Anthropic, Google, Ollama, Claude Code, Gemini CLI, Codex).
---

# Comanda - Declarative AI Pipelines

Comanda defines LLM workflows in YAML and runs them from the command line. Workflows can chain multiple AI models, run steps in parallel, and pipe data through processing stages.

## Installation

```bash
# macOS
brew install kris-hansen/comanda/comanda

# Or via Go
go install github.com/kris-hansen/comanda@latest
```

Then configure API keys:
```bash
comanda configure
```

## Commands

### Generate a Workflow

Create a workflow YAML from natural language:

```bash
comanda generate <output.yaml> "<prompt>"

# Examples
comanda generate summarize.yaml "Create a workflow that summarizes text input"
comanda generate review.yaml "Analyze code for bugs, then suggest fixes" -m claude-sonnet-4-20250514
```

### Visualize a Workflow

Display ASCII chart of workflow structure:

```bash
comanda chart <workflow.yaml>
comanda chart workflow.yaml --verbose
```

Shows step relationships, models used, input/output chains, and validity.

### Process/Execute a Workflow

Run a workflow file:

```bash
comanda process <workflow.yaml>

# With input
cat file.txt | comanda process analyze.yaml
echo "Design a REST API" | comanda process multi-agent.yaml

# Multiple workflows
comanda process step1.yaml step2.yaml step3.yaml
```

### View/Edit Workflows

Workflow files are YAML. Read them directly to understand or modify:

```bash
cat workflow.yaml
```

## Workflow YAML Format

### Basic Step

```yaml
step_name:
  input: STDIN | NA | filename | $VARIABLE
  model: gpt-4o | claude-sonnet-4-20250514 | gemini-pro | ollama/llama2 | claude-code | gemini-cli
  action: "Instruction for the model"
  output: STDOUT | filename | $VARIABLE
```

### Parallel Execution

```yaml
parallel-process:
  analysis-one:
    input: STDIN
    model: claude-sonnet-4-20250514
    action: "Analyze for security issues"
    output: $SECURITY

  analysis-two:
    input: STDIN
    model: gpt-4o
    action: "Analyze for performance"
    output: $PERF
```

### Chained Steps

```yaml
extract:
  input: document.pdf
  model: gpt-4o
  action: "Extract key points"
  output: $POINTS

summarize:
  input: $POINTS
  model: claude-sonnet-4-20250514
  action: "Create executive summary"
  output: STDOUT
```

### Generate + Process (Meta-workflows)

```yaml
create_workflow:
  input: NA
  generate:
    model: gpt-4o
    action: "Create a workflow that analyzes sentiment"
    output: generated.yaml

run_it:
  input: NA
  process:
    workflow_file: generated.yaml
```

## Available Models

Run `comanda configure` to set up API keys. Common models:

| Provider | Models |
|----------|--------|
| OpenAI | `gpt-4o`, `gpt-4o-mini`, `o1`, `o1-mini` |
| Anthropic | `claude-sonnet-4-20250514`, `claude-opus-4-20250514` |
| Google | `gemini-pro`, `gemini-flash` |
| Ollama | `ollama/llama2`, `ollama/mistral`, etc. |
| Agentic | `claude-code`, `gemini-cli`, `openai-codex` |

## Examples Location

See `~/clawd/comanda/examples/` for workflow samples:
- `agentic-loop/` - Autonomous agent patterns
- `claude-code/` - Claude Code integration
- `gemini-cli/` - Gemini CLI workflows
- `document-processing/` - PDF, text extraction
- `database-connections/` - DB query workflows

## Troubleshooting

- **"model not configured"**: Run `comanda configure` to add API keys
- **Workflow validation errors**: Use `comanda chart workflow.yaml` to visualize and check validity
- **Debug mode**: Add `--debug` flag for verbose logging
