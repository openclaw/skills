---
name: nomad
version: 1.0.0
description: Query HashiCorp Nomad clusters. List jobs, nodes, allocations, evaluations, and services. Read-only operations for monitoring and troubleshooting.
homepage: https://github.com/danfedick/nomad-skill
metadata: {"clawdbot":{"emoji":"📦","requires":{"bins":["nomad"]}}}
---

# Nomad Skill

Query HashiCorp Nomad clusters using the `nomad` CLI. Read-only operations for monitoring and troubleshooting.

## Requirements

- `nomad` CLI installed
- `NOMAD_ADDR` environment variable set (or defaults to http://127.0.0.1:4646)
- `NOMAD_TOKEN` if ACLs are enabled

## Commands

### Jobs

List all jobs:
```bash
nomad job status
```

Get job details:
```bash
nomad job status <job-id>
```

Job history:
```bash
nomad job history <job-id>
```

Job deployments:
```bash
nomad job deployments <job-id>
```

### Allocations

List allocations for a job:
```bash
nomad job allocs <job-id>
```

Allocation details:
```bash
nomad alloc status <alloc-id>
```

Allocation logs (stdout):
```bash
nomad alloc logs <alloc-id>
```

Allocation logs (stderr):
```bash
nomad alloc logs -stderr <alloc-id>
```

Follow logs:
```bash
nomad alloc logs -f <alloc-id>
```

### Nodes

List all nodes:
```bash
nomad node status
```

Node details:
```bash
nomad node status <node-id>
```

Node allocations:
```bash
nomad node status -allocs <node-id>
```

### Evaluations

List recent evaluations:
```bash
nomad eval list
```

Evaluation details:
```bash
nomad eval status <eval-id>
```

### Services

List services (Nomad native service discovery):
```bash
nomad service list
```

Service info:
```bash
nomad service info <service-name>
```

### Namespaces

List namespaces:
```bash
nomad namespace list
```

### Variables

List variables:
```bash
nomad var list
```

Get variable:
```bash
nomad var get <path>
```

### Cluster

Server members:
```bash
nomad server members
```

Agent info:
```bash
nomad agent-info
```

## JSON Output

Add `-json` to most commands for JSON output:
```bash
nomad job status -json
nomad node status -json
nomad alloc status -json <alloc-id>
```

## Filtering

Use `-filter` for expression-based filtering:
```bash
nomad job status -filter='Status == "running"'
nomad node status -filter='Status == "ready"'
```

## Common Patterns

### Find failed allocations
```bash
nomad job allocs <job-id> | grep -i failed
```

### Get logs from latest allocation
```bash
nomad alloc logs $(nomad job allocs -json <job-id> | jq -r '.[0].ID')
```

### Check cluster health
```bash
nomad server members
nomad node status
```

## Environment Variables

- `NOMAD_ADDR` — Nomad API address (default: http://127.0.0.1:4646)
- `NOMAD_TOKEN` — ACL token for authentication
- `NOMAD_NAMESPACE` — Default namespace
- `NOMAD_REGION` — Default region
- `NOMAD_CACERT` — Path to CA cert for TLS
- `NOMAD_CLIENT_CERT` — Path to client cert for TLS
- `NOMAD_CLIENT_KEY` — Path to client key for TLS

## Notes

- This skill is read-only. No job submissions, stops, or modifications.
- Use `nomad-tui` for interactive cluster management.
- For job deployment, use `nomad job run <file.nomad.hcl>` directly.
