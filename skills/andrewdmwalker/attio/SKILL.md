---
name: attio
description: Attio CRM integration for managing companies, people, deals, notes, tasks, and custom objects. Use when working with Attio CRM data, searching contacts, managing sales pipelines, adding notes to records, creating tasks, or syncing prospect information.
---

# Attio CRM

Manage Attio CRM via REST API. Supports companies, people, deals, lists (pipelines), notes, and tasks.

## Setup

Set `ATTIO_API_KEY` in environment or `~/.env`:
```bash
echo "ATTIO_API_KEY=your_api_key" >> ~/.env
```

Get your API key: Attio → Workspace Settings → Developers → New Access Token

## Quick Reference

### Objects (Records)

```bash
# List/search records
attio objects list                     # List available objects
attio records list <object>            # List records (companies, people, deals, etc.)
attio records search <object> <query>  # Search by text
attio records get <object> <id>        # Get single record
attio records create <object> <json>   # Create record
attio records update <object> <id> <json>  # Update record
```

### Lists (Pipelines)

```bash
attio lists list                       # Show all pipelines/lists
attio entries list <list_slug>         # List entries in a pipeline
attio entries add <list_slug> <object> <record_id>  # Add record to pipeline
```

### Notes

```bash
attio notes list <object> <record_id>  # Notes on a record
attio notes create <object> <record_id> <title> <content>
```

### Tasks

```bash
attio tasks list                       # All tasks
attio tasks create <content> [deadline]  # Create task (deadline: YYYY-MM-DD)
attio tasks complete <task_id>         # Mark complete
```

## Examples

### Find a company and add a note
```bash
# Search for company
attio records search companies "Acme"

# Add note to the company (using record_id from search)
attio notes create companies abc123-uuid "Call Notes" "Discussed Q1 roadmap..."
```

### Work with pipeline
```bash
# List pipeline stages
attio entries list sales_pipeline

# Add a company to pipeline
attio entries add sales_pipeline companies abc123-uuid
```

### Create a follow-up task
```bash
attio tasks create "Follow up with John at Acme" "2024-02-15"
```

## API Limits

- Rate limit: ~100 requests/minute
- Pagination: Use `limit` and `offset` params for large datasets

## Full API Docs

https://docs.attio.com/
