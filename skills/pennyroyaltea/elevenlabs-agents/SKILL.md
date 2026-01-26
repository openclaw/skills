---
name: elevenlabs-agents
description: Create, manage, and deploy ElevenLabs conversational AI agents. Use when the user wants to work with voice agents, list their agents, create new ones, or manage agent configurations.
metadata: {"clawdbot":{"requires":{"bins":["elevenlabs"]}}}
---

# ElevenLabs Agents Management

Manage ElevenLabs conversational AI agents on behalf of the user. Use the `elevenlabs` CLI internally but NEVER expose CLI commands or errors directly to the user.

## Critical Behavior Rules

1. **Hide CLI details**: Never tell users to run commands. Handle everything silently.
2. **Handle errors gracefully**: If a command fails, fix it yourself or explain the situation in user-friendly terms.
3. **Local vs Remote distinction**: Always be clear whether you're showing local (synced) agents or remote (platform) agents.

## Before Any Operation

Run these checks silently before attempting any agent operation:

### 1. Check authentication
```bash
elevenlabs auth whoami
```
If not authenticated, tell the user: "You're not logged into ElevenLabs. I'll need your API key to continue." Then run `elevenlabs auth login` and guide them through it.

### 2. Check project initialization
Look for `agents.json` in the working directory. If missing, silently run:
```bash
elevenlabs agents init
```
Never tell the user about missing `agents.json` - just initialize.

## Operations

### Listing Agents

When user asks to see their agents:

1. First try `elevenlabs agents list` (shows local agents)
2. If no local agents exist, tell user: "You have no local agents synced. Would you like me to pull your agents from ElevenLabs?"
3. If they confirm, run `elevenlabs agents pull` then list again
4. Present results in a clean table/list format, not raw CLI output

### Creating Agents

When user wants to create an agent:

1. Ask for agent name and purpose (don't mention "templates")
2. Based on their description, choose appropriate template:
   - Customer support → `customer-service`
   - General assistant → `assistant`
   - Voice-focused → `voice-only`
   - Simple/minimal → `minimal`
   - Default for unclear cases → `default`
3. Run: `elevenlabs agents add "Name" --template <template>`
4. Inform user the agent was created locally
5. Ask: "Would you like me to deploy this to ElevenLabs now?"
6. If yes, run `elevenlabs agents push`

### Syncing Agents

**Pull (remote → local):**
```bash
elevenlabs agents pull                    # all agents
elevenlabs agents pull --agent <id>       # specific agent
elevenlabs agents pull --update           # overwrite local with remote
```
Tell user: "I've synced your agents from ElevenLabs."

**Push (local → remote):**
```bash
elevenlabs agents push --dry-run  # preview first, check for issues
elevenlabs agents push            # actual push
```
Tell user: "I've deployed your changes to ElevenLabs."

### Checking Status

```bash
elevenlabs agents status
```
Present as: "Here's the sync status of your agents:" followed by a clean summary.

### Adding Tools to Agents

When user wants to add integrations/tools:
1. Ask what the tool should do
2. Ask for the webhook URL or configuration
3. Create config file and run:
```bash
elevenlabs agents tools add "Tool Name" --type webhook --config-path ./config.json
```
4. Push changes: `elevenlabs agents push`

### Getting Embed Code

```bash
elevenlabs agents widget <agent_id>
```
Present the HTML snippet cleanly, explain where to paste it.

## User-Friendly Language

| Instead of saying... | Say... |
|---------------------|--------|
| "Run `elevenlabs auth login`" | "I'll need to connect to your ElevenLabs account." |
| "No agents.json found" | (silently initialize, say nothing) |
| "Push failed" | "I couldn't deploy the changes. Let me check what went wrong..." |
| "You have 0 agents" | "You don't have any agents synced locally. Want me to check ElevenLabs for existing agents?" |
| "Agent created locally" | "I've created your agent. Would you like to deploy it now?" |

## Project Files (internal reference)

After initialization, the working directory contains:
- `agents.json` - Agent registry
- `agent_configs/` - Agent configuration files
- `tools.json` - Tool registry
- `tool_configs/` - Tool configurations

These are implementation details - don't mention them to users unless they specifically ask about project structure.
