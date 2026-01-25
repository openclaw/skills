---
name: n8n
description: Manage n8n workflows and automations via API. Use when working with n8n workflows, executions, or automation tasks - listing workflows, activating/deactivating, checking execution status, manually triggering workflows, or debugging automation issues.
---

# n8n Workflow Management

Interact with n8n automation platform via REST API.

## Setup

**First-time setup:**

1. Install dependencies (virtual environment):

```bash
cd skills/n8n-1.0.2
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables in `~/.zshrc` (or `~/.bashrc`):

```bash
export N8N_API_KEY="your-api-key-here"
export N8N_BASE_URL="https://your-n8n-instance.com"
```

3. Reload shell and verify connection:

```bash
source ~/.zshrc
./skills/n8n-1.0.2/scripts/n8n.sh list-workflows --pretty
```

> **Tip**: Get your API key from n8n UI: Settings → API

## Quick Reference

### List Workflows

```bash
./scripts/n8n.sh list-workflows --pretty
./scripts/n8n.sh list-workflows --active true --pretty
```

### Get Workflow Details

```bash
./scripts/n8n.sh get-workflow --id <workflow-id> --pretty
```

### Activate/Deactivate

```bash
./scripts/n8n.sh activate --id <workflow-id>
./scripts/n8n.sh deactivate --id <workflow-id>
```

### Executions

```bash
# List recent executions
./scripts/n8n.sh list-executions --limit 10 --pretty

# Get execution details
./scripts/n8n.sh get-execution --id <execution-id> --pretty

# Filter by workflow
./scripts/n8n.sh list-executions --id <workflow-id> --limit 20 --pretty
```

### Manual Execution

```bash
# Trigger workflow
./scripts/n8n.sh execute --id <workflow-id>

# With data
./scripts/n8n.sh execute --id <workflow-id> --data '{"key": "value"}'
```

## Python API

For programmatic access:

```python
from scripts.n8n_api import N8nClient

client = N8nClient()

# List workflows
workflows = client.list_workflows(active=True)

# Get workflow
workflow = client.get_workflow('workflow-id')

# Activate/deactivate
client.activate_workflow('workflow-id')
client.deactivate_workflow('workflow-id')

# Executions
executions = client.list_executions(workflow_id='workflow-id', limit=10)
execution = client.get_execution('execution-id')

# Execute workflow
result = client.execute_workflow('workflow-id', data={'key': 'value'})
```

## Common Tasks

### Debug Failed Workflows

1. List recent executions with failures
2. Get execution details to see error
3. Check workflow configuration
4. Deactivate if needed

### Monitor Workflow Health

1. List active workflows
2. Check recent execution status
3. Review error patterns

### Workflow Management

1. List all workflows
2. Review active/inactive status
3. Activate/deactivate as needed
4. Delete old workflows

## API Reference

For detailed API documentation, see [references/api.md](references/api.md).

## Troubleshooting

**Authentication error:**

- Verify N8N_API_KEY is set: `echo $N8N_API_KEY`
- Check API key is valid in n8n UI

**Connection error:**

- Check N8N_BASE_URL if using custom URL

**Command errors:**

- Use `--pretty` flag for readable output
- Check `--id` is provided when required
- Validate JSON format for `--data` parameter
