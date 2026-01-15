---
name: servicenow-agent
description: Read-only access to ServiceNow Table API using basic auth for querying records and identifying data.
read_when:
  - Need to read ServiceNow Table API records
  - Need to query a table or fetch a record by sys_id
metadata: {"clawdbot":{"emoji":"🧾","requires":{"bins":["node"]}}}
---

# ServiceNow Table API (Read-Only)

Use this skill to **read** data from ServiceNow via the Table API. **Do not** create, update, or delete records.

## Configuration (required)

Set these environment variables (see `.env` in this folder):

- `SERVICENOW_DOMAIN` — instance domain (e.g., `myinstance.service-now.com`)
- `SERVICENOW_USERNAME` — username for basic auth
- `SERVICENOW_PASSWORD` — password for basic auth

If your domain already includes `https://`, use it as-is. Otherwise, requests should be made to:

```
https://$SERVICENOW_DOMAIN
```

## Allowed Operations (GET only)

Use **only** the GET endpoints from `openapi.yaml`:

1. **List records**
   - `GET /api/now/table/{tableName}`
2. **Get a record by sys_id**
   - `GET /api/now/table/{tableName}/{sys_id}`

Never use `POST`, `PUT`, `PATCH`, or `DELETE`.

## Common Query Params

- `sysparm_query` — encoded query (e.g., `active=true^priority=1`)
- `sysparm_fields` — comma-separated fields to return
- `sysparm_limit` — limit record count (keep small for safety)
- `sysparm_display_value` — `true` | `false` | `all`
- `sysparm_exclude_reference_link` — `true` to reduce clutter

See `openapi.yaml` for the full list of parameters.

## CLI (required)

Use the bundled CLI for **all** reads (GET only). It pulls auth from `.env` by default and lets you override with flags.

### Command overview

- `list <table>` — list records from a table
- `get <table> <sys_id>` — fetch one record by sys_id
- `batch <file.json>` — run multiple read requests in one call (specialists)

### Auth flags (override `.env`)

- `--domain <domain>` — instance domain (with or without `https://`)
- `--username <user>` (alias: `--user`)
- `--password <pass>` (alias: `--pass`)

### Query flags

Use any of these as `--sysparm_*` flags:

- `--sysparm_query`
- `--sysparm_fields`
- `--sysparm_limit`
- `--sysparm_display_value`
- `--sysparm_exclude_reference_link`
- `--sysparm_suppress_pagination_header`
- `--sysparm_view`
- `--sysparm_query_category`
- `--sysparm_query_no_domain`
- `--sysparm_no_count`

### Output

- `--pretty` — pretty-print JSON output

### Examples

List recent incidents:

```bash
node cli.mjs list incident --sysparm_limit 5 --sysparm_fields number,short_description,priority,sys_id
```

Query with a filter:

```bash
node cli.mjs list cmdb_ci --sysparm_query "operational_status=1^install_status=1" --sysparm_limit 10
```

Fetch a single record:

```bash
node cli.mjs get incident <sys_id> --sysparm_fields number,short_description,opened_at
```

Override auth on the fly:

```bash
node cli.mjs list incident --domain myinstance.service-now.com --username admin --password "***" --sysparm_limit 3
```

### Specialist presets (combine multiple reads)

Create JSON batch files under `specialists/` to run multiple reads at once. Example file included:

- `specialists/incidents.json`

Each entry supports the same `sysparm_*` fields from `openapi.yaml` plus:

- `name` — label in the batch output
- `table` — target table (required)
- `sys_id` — optional single-record fetch

Run a batch preset:

```bash
node cli.mjs batch specialists/incidents.json --pretty
```

## Output

The Table API returns JSON by default. Expect results under `result`.

## Notes

- Keep result sizes small with `sysparm_limit`.
- Use `sysparm_fields` to avoid large payloads.
- This skill is **read-only** by design.
