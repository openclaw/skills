---
name: zoho
description: Interact with Zoho CRM and Zoho Projects APIs. Use when managing deals, contacts, leads, tasks, projects, milestones, or any Zoho workspace data. Triggers on mentions of Zoho, CRM, deals, pipeline, projects, tasks, milestones.
---

# Zoho Integration (CRM + Projects)

## Quick Start

Use the `zoho` CLI wrapper — it handles OAuth token refresh and caching automatically.

```bash
zoho help          # Show all commands
zoho token         # Print current access token (auto-refreshes)
```

## Authentication

Credentials stored in `/root/clawd/skills/zoho/.env`:
```
ZOHO_CLIENT_ID=...
ZOHO_CLIENT_SECRET=...
ZOHO_REFRESH_TOKEN=...
ZOHO_ORG_ID=...
ZOHO_API_DOMAIN=https://www.zohoapis.com
ZOHO_ACCOUNTS_URL=https://accounts.zoho.com
```

- Access tokens auto-refresh and cache for 50 minutes
- Token cache: `/root/clawd/skills/zoho/.token_cache`
- API domain varies by datacenter (.com, .eu, .in, .com.au, .jp)

### First-time setup
1. Register at https://api-console.zoho.com/ → Server-based app
2. Get auth code → exchange for refresh token
3. Store credentials in `.env`

## CRM Commands

```bash
# List records from any module
zoho crm list Deals
zoho crm list Deals "page=1&per_page=5&sort_by=Created_Time&sort_order=desc"
zoho crm list Contacts
zoho crm list Leads

# Get a specific record
zoho crm get Deals 1234567890

# Search with criteria
zoho crm search Deals "(Stage:equals:Closed Won)"
zoho crm search Contacts "(Email:contains:@acme.com)"
zoho crm search Leads "(Lead_Source:equals:Web)"

# Create a record
zoho crm create Contacts '{"data":[{"Last_Name":"Smith","First_Name":"John","Email":"j@co.com"}]}'
zoho crm create Deals '{"data":[{"Deal_Name":"New Project","Stage":"Qualification","Amount":50000}]}'

# Update a record
zoho crm update Deals 1234567890 '{"data":[{"Stage":"Closed Won"}]}'

# Delete a record
zoho crm delete Deals 1234567890
```

### CRM Modules
Leads, Contacts, Accounts, Deals, Tasks, Events, Calls, Notes, Products, Quotes, Sales_Orders, Purchase_Orders, Invoices

### Search Operators
equals, not_equal, starts_with, contains, not_contains, in, not_in, between, greater_than, less_than

## Projects Commands

```bash
# List all projects
zoho proj list

# Get project details
zoho proj get 12345678

# Tasks
zoho proj tasks 12345678
zoho proj create-task 12345678 "name=Fix+login+bug&priority=High&start_date=01-27-2026"
zoho proj update-task 12345678 98765432 "percent_complete=50"

# Other
zoho proj milestones 12345678
zoho proj tasklists 12345678
zoho proj bugs 12345678
zoho proj timelogs 12345678
```

### Task Fields
name, start_date (MM-DD-YYYY), end_date, priority (None/Low/Medium/High), owner, description, tasklist_id, percent_complete

## Raw API Calls

For anything not covered by subcommands:
```bash
# Get field definitions for a module
zoho raw GET /crm/v7/settings/fields?module=Deals

# Get org info
zoho raw GET /crm/v7/org

# Custom modules
zoho raw GET /crm/v7/Custom_Module
```

## Usage Patterns

### When Shreef asks about deals/pipeline
```bash
zoho crm list Deals "sort_by=Created_Time&sort_order=desc&per_page=10" | jq '.data[] | {Deal_Name, Stage, Amount, Closing_Date}'
```

### When checking project progress
```bash
# Get all projects, then drill into tasks
zoho proj list | jq '.projects[] | {name, status, id: .id_string}'
zoho proj tasks <project_id> | jq '.tasks[] | {name, status: .status.name, percent_complete, priority}'
```

### When creating tasks from conversation
```bash
zoho proj create-task <project_id> "name=Task+description&priority=High&start_date=MM-DD-YYYY&end_date=MM-DD-YYYY"
```

## Rate Limits
- CRM: 100 requests/min
- Projects: varies by plan
- Token refresh: don't call more than needed (cached automatically)

## References
- [CRM API Fields](references/crm-api.md)
- [Projects API Endpoints](references/projects-api.md)
