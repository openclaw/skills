---
name: salesforce-dx
description: Query Salesforce data and manage sales pipelines using the `sf` CLI. Use for SOQL queries (simple to complex), opportunity pipeline analysis, forecast reporting, data exports, schema exploration, and CRM data operations. Also use for executive workflows like looking up deals by name, finding contact info to email prospects, preparing pipeline reviews, and cross-referencing CRM data with other tools. Triggers on Salesforce, SOQL, pipeline, opportunity, forecast, CRM data, deal lookup, prospect email, account info, or sf CLI questions.
---

# Salesforce DX — Data & Pipeline

Query data and manage pipelines with the `sf` CLI.

## Prerequisites

```bash
# Verify CLI and auth
sf --version
sf org list
```

If no orgs listed, authenticate:
```bash
sf org login web --alias my-org --set-default
```

## Schema Discovery

Before querying, explore available objects and fields:

```bash
# List all objects
sf sobject list --target-org my-org

# Describe object fields
sf sobject describe --sobject Opportunity --target-org my-org

# Quick field list (names only)
sf sobject describe --sobject Opportunity --target-org my-org | grep -E "^name:|^type:" 
```

## SOQL Queries

### Basic Patterns

```bash
# Simple query
sf data query -q "SELECT Id, Name, Amount FROM Opportunity LIMIT 10"

# With WHERE clause
sf data query -q "SELECT Id, Name FROM Opportunity WHERE StageName = 'Closed Won'"

# Date filtering
sf data query -q "SELECT Id, Name FROM Opportunity WHERE CloseDate = THIS_QUARTER"

# Export to CSV
sf data query -q "SELECT Id, Name, Amount FROM Opportunity" --result-format csv > opps.csv
```

### Relationships

```bash
# Parent lookup (Account from Opportunity)
sf data query -q "SELECT Id, Name, Account.Name, Account.Industry FROM Opportunity"

# Child subquery (Opportunities from Account)
sf data query -q "SELECT Id, Name, (SELECT Id, Name, Amount FROM Opportunities) FROM Account LIMIT 5"
```

### Aggregations

```bash
# COUNT
sf data query -q "SELECT COUNT(Id) total FROM Opportunity WHERE IsClosed = false"

# SUM and GROUP BY
sf data query -q "SELECT StageName, SUM(Amount) total FROM Opportunity GROUP BY StageName"

# Multiple aggregates
sf data query -q "SELECT StageName, COUNT(Id) cnt, SUM(Amount) total, AVG(Amount) avg FROM Opportunity GROUP BY StageName"
```

### Bulk Queries (Large Datasets)

```bash
# Use --bulk for >2000 records
sf data query -q "SELECT Id, Name, Amount FROM Opportunity" --bulk --wait 10
```

## Pipeline Management

### Pipeline Snapshot

```bash
# Open pipeline by stage
sf data query -q "SELECT StageName, COUNT(Id) cnt, SUM(Amount) total FROM Opportunity WHERE IsClosed = false GROUP BY StageName ORDER BY StageName"

# Pipeline by owner
sf data query -q "SELECT Owner.Name, SUM(Amount) total FROM Opportunity WHERE IsClosed = false GROUP BY Owner.Name ORDER BY SUM(Amount) DESC"

# Pipeline by close month
sf data query -q "SELECT CALENDAR_MONTH(CloseDate) month, SUM(Amount) total FROM Opportunity WHERE IsClosed = false AND CloseDate = THIS_YEAR GROUP BY CALENDAR_MONTH(CloseDate) ORDER BY CALENDAR_MONTH(CloseDate)"
```

### Win/Loss Analysis

```bash
# Win rate by stage
sf data query -q "SELECT StageName, COUNT(Id) FROM Opportunity WHERE IsClosed = true GROUP BY StageName"

# Closed won this quarter
sf data query -q "SELECT Id, Name, Amount, CloseDate FROM Opportunity WHERE StageName = 'Closed Won' AND CloseDate = THIS_QUARTER ORDER BY Amount DESC"

# Lost deals with reasons
sf data query -q "SELECT Id, Name, Amount, StageName, Loss_Reason__c FROM Opportunity WHERE StageName = 'Closed Lost' AND CloseDate = THIS_QUARTER"
```

### Forecast Queries

```bash
# Weighted pipeline (assumes Probability field)
sf data query -q "SELECT StageName, SUM(Amount) gross, SUM(ExpectedRevenue) weighted FROM Opportunity WHERE IsClosed = false GROUP BY StageName"

# Deals closing this month
sf data query -q "SELECT Id, Name, Amount, StageName, CloseDate FROM Opportunity WHERE CloseDate = THIS_MONTH AND IsClosed = false ORDER BY Amount DESC"

# Stale deals (no activity in 30 days)
sf data query -q "SELECT Id, Name, Amount, LastActivityDate FROM Opportunity WHERE IsClosed = false AND LastActivityDate < LAST_N_DAYS:30"
```

## Data Operations

### Create Records

```bash
sf data create record -s Opportunity -v "Name='New Deal' StageName='Prospecting' CloseDate=2024-12-31 Amount=50000"
```

### Update Records

```bash
# By ID
sf data update record -s Opportunity -i 006xx000001234 -v "StageName='Negotiation'"

# Bulk update via CSV
sf data upsert bulk -s Opportunity -f updates.csv -i Id --wait 10
```

### Export/Import

```bash
# Export with relationships
sf data export tree -q "SELECT Id, Name, (SELECT Id, Subject FROM Tasks) FROM Account WHERE Industry = 'Technology'" -d ./export

# Import
sf data import tree -f ./export/Account.json
```

## JSON Output for Scripting

Add `--json` for structured output:

```bash
sf data query -q "SELECT Id, Name, Amount FROM Opportunity WHERE IsClosed = false" --json
```

Parse with jq:
```bash
sf data query -q "SELECT Id, Name FROM Opportunity LIMIT 5" --json | jq '.result.records[].Name'
```

## Common Date Literals

| Literal | Meaning |
|---------|---------|
| TODAY | Current day |
| THIS_WEEK | Current week |
| THIS_MONTH | Current month |
| THIS_QUARTER | Current quarter |
| THIS_YEAR | Current year |
| LAST_N_DAYS:n | Past n days |
| NEXT_N_DAYS:n | Next n days |
| LAST_QUARTER | Previous quarter |

## Troubleshooting

**"Malformed query"** — Check field API names (not labels). Use `sf sobject describe` to verify.

**"QUERY_TIMEOUT"** — Add filters, use `--bulk`, or add `LIMIT`.

**"INVALID_FIELD"** — Field may not exist on that object or your profile lacks access.

**Large result sets** — Use `--bulk` flag for queries returning >2000 records.

## Executive Workflows

### Quick Deal Lookup

Find a deal by name or account:
```bash
# By opportunity name (fuzzy)
sf data query -q "SELECT Id, Name, Amount, StageName, CloseDate, Owner.Name, Account.Name FROM Opportunity WHERE Name LIKE '%Acme%' ORDER BY Amount DESC"

# By account name
sf data query -q "SELECT Id, Name, Amount, StageName, CloseDate FROM Opportunity WHERE Account.Name LIKE '%Microsoft%' AND IsClosed = false"

# Recent deals I own
sf data query -q "SELECT Id, Name, Amount, StageName, CloseDate, Account.Name FROM Opportunity WHERE OwnerId = '<my-user-id>' AND IsClosed = false ORDER BY CloseDate"
```

### Get Contact Info for Outreach

Find someone to email at a company:
```bash
# Contacts at an account
sf data query -q "SELECT Id, Name, Email, Phone, Title FROM Contact WHERE Account.Name LIKE '%Acme%'"

# Decision makers (by title)
sf data query -q "SELECT Name, Email, Title, Account.Name FROM Contact WHERE Title LIKE '%CEO%' OR Title LIKE '%VP%' OR Title LIKE '%Director%'"

# Contacts on a specific deal
sf data query -q "SELECT Contact.Name, Contact.Email, Contact.Title, Role FROM OpportunityContactRole WHERE Opportunity.Name LIKE '%Acme%'"
```

### Prep for Pipeline Review

Get a quick executive summary:
```bash
# Top 10 deals closing this quarter
sf data query -q "SELECT Name, Account.Name, Amount, StageName, CloseDate, Owner.Name FROM Opportunity WHERE CloseDate = THIS_QUARTER AND IsClosed = false ORDER BY Amount DESC LIMIT 10"

# Deals by rep (for 1:1s)
sf data query -q "SELECT Owner.Name, COUNT(Id) deals, SUM(Amount) total FROM Opportunity WHERE IsClosed = false GROUP BY Owner.Name ORDER BY SUM(Amount) DESC"

# Deals needing attention (stale)
sf data query -q "SELECT Name, Amount, StageName, LastActivityDate, Owner.Name FROM Opportunity WHERE IsClosed = false AND LastActivityDate < LAST_N_DAYS:14 ORDER BY Amount DESC LIMIT 10"
```

### Account Intelligence

Before a call or meeting:
```bash
# Account overview
sf data query -q "SELECT Id, Name, Industry, BillingCity, Website, OwnerId FROM Account WHERE Name LIKE '%Acme%'"

# All open deals with account
sf data query -q "SELECT Name, Amount, StageName, CloseDate FROM Opportunity WHERE Account.Name LIKE '%Acme%' AND IsClosed = false"

# Recent activities
sf data query -q "SELECT Subject, Status, ActivityDate FROM Task WHERE Account.Name LIKE '%Acme%' ORDER BY ActivityDate DESC LIMIT 5"
```

### Cross-Tool Workflows

**Salesforce + Email (via gog/gmail):**
1. Find contact email: `sf data query -q "SELECT Email FROM Contact WHERE Account.Name LIKE '%Acme%'"`
2. Draft email using that address with your email tool

**Salesforce + Calendar:**
1. Find deals closing soon: `sf data query -q "SELECT Name, Account.Name, CloseDate FROM Opportunity WHERE CloseDate = THIS_WEEK"`
2. Cross-reference with calendar to ensure follow-ups scheduled

**Quick CRM Update After Call:**
```bash
# Log a task
sf data create record -s Task -v "Subject='Call with John' WhatId='<opportunity-id>' Status='Completed' ActivityDate=$(date +%Y-%m-%d)"

# Update opportunity stage
sf data update record -s Opportunity -i <opp-id> -v "StageName='Negotiation' NextStep='Send proposal'"
```

### Finding Your User ID

Needed for "deals I own" queries:
```bash
sf data query -q "SELECT Id, Name FROM User WHERE Email = 'your.email@company.com'"
```

Store this in your local config for quick reference.

## References

- **[soql-patterns.md](references/soql-patterns.md)** — Advanced SOQL patterns (polymorphic, semi-joins, formula fields)
- **[pipeline-queries.md](references/pipeline-queries.md)** — Ready-to-use pipeline and forecast queries
