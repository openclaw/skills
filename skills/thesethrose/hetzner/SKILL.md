---
name: hetzner
description: Hetzner Cloud server management using the hcloud CLI. Manage servers, networks, volumes, firewalls, floating IPs, and SSH keys.
metadata: {"clawdbot":{"emoji":"🖥️","requires":{"bins":["hcloud"]},"env":{"HCLOUD_TOKEN":"Hetzner Cloud API token"}}}
---

# Hetzner Cloud Skill

Manage your Hetzner Cloud infrastructure using the `hcloud` CLI.

## Setup

Set your Hetzner Cloud API token:
```bash
export HCLOUD_TOKEN="your_token_here"
```

Or add it to the skill's `.env` file.

## Usage

Common commands:

### Servers
- `servers list` - List all servers
- `servers get <id>` - Get server details
- `servers create <name> <type> <image> <location>` - Create a server
- `servers delete <id>` - Delete a server
- `servers start <id>` - Start server
- `servers stop <id>` - Stop server
- `servers reboot <id>` - Reboot server
- `servers ssh <id>` - SSH into server

### Networks
- `networks list` - List networks
- `networks get <id>` - Get network details

### Floating IPs
- `floating-ips list` - List floating IPs

### SSH Keys
- `ssh-keys list` - List SSH keys

### Volumes
- `volumes list` - List volumes

### Firewalls
- `firewalls list` - List firewalls

## Example Usage

```
You: List my Hetzner servers
Bot: Runs servers list → Shows all your cloud servers

You: Create a new server for testing
Bot: Runs servers create test-server cx11 debian-11 fsn1

You: What's using the most resources?
Bot: Runs servers list and analyzes resource usage
```

**Note:** Requires `HCLOUD_TOKEN` environment variable.
