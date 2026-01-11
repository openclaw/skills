# Clawdbot Documentation Expert

Use this skill when the user wants to learn about Clawdbot features, configuration, or troubleshooting. You become an expert on the Clawdbot documentation.

## How to Use

1. **Fetch the sitemap** to get the current documentation structure
2. **Present topic categories** to the user
3. **Read specific docs** based on user interest
4. **Answer follow-up questions** with documentation references

## Step 1: Fetch Current Sitemap

Always start by fetching the live sitemap to get up-to-date documentation:

```bash
curl -s https://docs.clawd.bot/sitemap.xml | grep -oP '(?<=<loc>)[^<]+' | sort
```

## Step 2: Documentation Categories

The docs are organized into these main sections:

### 🚀 Getting Started (`/start/`)
- getting-started, onboarding, setup, wizard, pairing
- clawd, hubs, faq, lore, showcase

### 🔧 Gateway & Operations (`/gateway/`)
- configuration, configuration-examples, authentication
- health, heartbeat, logging, troubleshooting
- remote, tailscale, sandboxing, security
- doctor, discovery, bonjour, pairing

### 💬 Providers (`/providers/`)
- discord, telegram, whatsapp, slack, signal
- imessage, msteams, grammy
- troubleshooting, location

### 🧠 Core Concepts (`/concepts/`)
- agent, agent-loop, agent-workspace, multi-agent
- session, sessions, session-tool, session-pruning
- messages, group-messages, groups
- models, model-providers, model-failover
- queue, retry, streaming, typing-indicators
- system-prompt, timezone, oauth, presence
- architecture, compaction, usage-tracking

### 🛠️ Tools (`/tools/`)
- bash, browser, skills, skills-config
- elevated, reactions, slash-commands
- subagents, thinking, clawdhub, agent-send

### ⚡ Automation (`/automation/`)
- cron-jobs, webhook, poll
- gmail-pubsub, auth-monitoring

### 💻 CLI (`/cli/`)
- gateway, message, sandbox, update

### 📱 Platforms (`/platforms/`)
- macos, linux, windows, ios, android, hetzner
- Mac-specific: bundled-gateway, canvas, child-process, webchat, voice-overlay, voicewake, permissions, etc.

### 📡 Nodes (`/nodes/`)
- camera, audio, images, location-command, talk, voicewake

### 🌐 Web (`/web/`)
- webchat, dashboard, control-ui

### 📦 Install (`/install/`)
- docker, ansible, bun, nix, updating

### 📚 Reference (`/reference/`)
- AGENTS.default, RELEASING, rpc, device-models
- Templates: AGENTS, BOOTSTRAP, HEARTBEAT, IDENTITY, SOUL, TOOLS, USER

## Step 3: Read Specific Documentation

When the user wants details on a topic, fetch it with the browser:

```
Use pi_browser to navigate to the specific doc URL, then snapshot to read it.
```

Example URLs:
- https://docs.clawd.bot/providers/discord
- https://docs.clawd.bot/concepts/queue
- https://docs.clawd.bot/gateway/configuration

## Workflow Example

**User:** "Tell me about Clawdbot"

**You:** Present the high-level categories above and ask which area interests them.

**User:** "I want to learn about Discord setup"

**You:** Navigate to https://docs.clawd.bot/providers/discord, read it, and explain the key points.

**User:** "How do I configure requireMention?"

**You:** Reference the specific section from the Discord docs and provide the config example.

## Tips

- Always cite the specific doc URL when answering
- If docs have changed, re-fetch the sitemap
- For complex topics, offer to read multiple related docs
- Provide code/config examples directly from the docs
