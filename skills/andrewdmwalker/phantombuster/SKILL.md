---
name: phantombuster
description: Control PhantomBuster automation agents via API. List agents, launch automations, get output/results, check status, and abort running agents. Use when the user needs to run LinkedIn scraping, Twitter automation, lead generation phantoms, or any PhantomBuster workflow.
version: 1.0.0
author: captmarbles
---

# PhantomBuster Skill

Control your [PhantomBuster](https://phantombuster.com) automation agents from the command line.

## Setup

1. Get your API key from [Workspace Settings](https://phantombuster.com/workspace-settings)
2. Set the environment variable:
   ```bash
   export PHANTOMBUSTER_API_KEY=your-api-key-here
   ```

## Usage

All commands use the bundled `pb.py` script in this skill's directory.

### List Agents

See all your configured PhantomBuster agents.

```bash
python3 pb.py list
python3 pb.py list --json  # JSON output
```

### Launch an Agent

Start a phantom by ID or name.

```bash
python3 pb.py launch <agent-id>
python3 pb.py launch <agent-id> --argument '{"search": "CEO fintech"}'
```

### Get Agent Output

Fetch the results/output from the most recent run.

```bash
python3 pb.py output <agent-id>
python3 pb.py output <agent-id> --json  # Raw JSON
```

### Check Agent Status

See if an agent is running, finished, or errored.

```bash
python3 pb.py status <agent-id>
```

### Abort Running Agent

Stop an agent that's currently running.

```bash
python3 pb.py abort <agent-id>
```

### Get Agent Details

Full details about a specific agent.

```bash
python3 pb.py get <agent-id>
```

## Example Prompts

- *"List my PhantomBuster agents"*
- *"Launch my LinkedIn Sales Navigator scraper"*
- *"Get the output from agent 12345"*
- *"Check if my Twitter follower phantom is still running"*
- *"Abort the currently running agent"*

## Common Phantoms

PhantomBuster offers many pre-built automations:
- **LinkedIn Sales Navigator Search** — Extract leads from searches
- **LinkedIn Profile Scraper** — Get profile data
- **Twitter Follower Collector** — Scrape followers
- **Instagram Profile Scraper** — Get IG profile data
- **Google Maps Search Export** — Extract business listings

## Rate Limits

PhantomBuster has execution time limits based on your plan. The API itself is not heavily rate-limited, but agent execution consumes your plan's minutes.
