# Comanda Workflow Specification

Complete reference for YAML workflow syntax.

## Step Types

### Standard Step

```yaml
step_name:
  input: <source>
  model: <model-id>
  action: "Instruction text"
  output: <destination>
```

### Generate Step (Create Workflow)

```yaml
step_name:
  input: <source>
  generate:
    model: <model-id>
    action: "Describe the workflow to create"
    output: <filename.yaml>
```

### Process Step (Execute Workflow)

```yaml
step_name:
  input: <source>
  process:
    workflow_file: <filename.yaml>
```

### Defer Step (Human-in-the-loop)

```yaml
step_name:
  input: $PREVIOUS
  defer:
    message: "Review and approve this output"
    output: $APPROVED
```

## Input Sources

| Value | Description |
|-------|-------------|
| `STDIN` | Read from standard input |
| `NA` | No input required |
| `filename.txt` | Read from file |
| `$VARIABLE` | Use variable from previous step |
| `URL:https://...` | Fetch from URL |

## Output Destinations

| Value | Description |
|-------|-------------|
| `STDOUT` | Print to standard output |
| `filename.txt` | Write to file |
| `$VARIABLE` | Store in variable for next step |

## Parallel Execution

Wrap steps in `parallel-process:` to run concurrently:

```yaml
parallel-process:
  step-a:
    input: STDIN
    model: gpt-4o
    action: "Task A"
    output: $RESULT_A

  step-b:
    input: STDIN
    model: claude-sonnet-4-20250514
    action: "Task B"
    output: $RESULT_B

combine:
  input: "$RESULT_A\n$RESULT_B"
  model: gpt-4o
  action: "Synthesize results"
  output: STDOUT
```

## Conditional Logic

Use model output to branch:

```yaml
classify:
  input: STDIN
  model: gpt-4o
  action: "Classify as: BUG, FEATURE, or QUESTION. Reply with only the classification."
  output: $TYPE

handle:
  input: "$TYPE: $STDIN"
  model: claude-sonnet-4-20250514
  action: "Handle based on the classification type"
  output: STDOUT
```

## Multi-file Processing

```bash
# Process multiple files
for f in *.txt; do
  cat "$f" | comanda process analyze.yaml > "${f%.txt}.analysis.md"
done

# Or use shell expansion in workflow
comanda process batch.yaml --input "docs/*.md"
```

## Environment Variables

Workflows can reference environment variables:

```yaml
step:
  input: NA
  model: gpt-4o
  action: "API endpoint is ${API_URL}"
  output: STDOUT
```

## Agentic Models

Special models that run external tools:

```yaml
code_review:
  input: STDIN
  model: claude-code
  action: "Review this code and suggest improvements"
  output: $REVIEW
```

Agentic models: `claude-code`, `gemini-cli`, `openai-codex`

These models can execute commands, edit files, and interact with the filesystem.
