---
name: rei
description: Set up Rei Qwen3 Coder as a model provider. Use when configuring coder.reilabs.org, adding Rei to Clawdbot, or troubleshooting 403 errors from Rei endpoints.
---

# Rei Qwen3 Coder

Rei provides Qwen3 Coder via an OpenAI-compatible endpoint at `coder.reilabs.org`.

## Setup via Script

```bash
./skills/rei/scripts/setup.sh YOUR_REI_API_KEY
```

This adds the provider, adds it to the model allowlist, and restarts the gateway.

## Setup via Agent

Ask your agent:

> "Set up Rei with API key: YOUR_KEY"

The agent will read this skill and run the setup script for you.

## Switching Models

**Via chat:**
```
/model rei
/model opus
```

**Via script:**
```bash
./skills/rei/scripts/switch.sh rei
./skills/rei/scripts/switch.sh opus
```

**Via agent:**
> "Switch to Rei" or "Switch back to Opus"

## Revert

If something breaks, restore the backup:

```bash
./skills/rei/scripts/revert.sh
```

## Manual Setup

Add to `~/.clawdbot/clawdbot.json`:

```json
{
  "models": {
    "providers": {
      "rei": {
        "baseUrl": "https://coder.reilabs.org/v1",
        "apiKey": "YOUR_API_KEY",
        "api": "openai-completions",
        "headers": { "User-Agent": "Clawdbot/1.0" },
        "models": [{
          "id": "rei-qwen3-coder",
          "name": "Rei Qwen3 Coder",
          "contextWindow": 200000,
          "maxTokens": 8192
        }]
      }
    }
  },
  "agents": {
    "defaults": {
      "models": {
        "rei/rei-qwen3-coder": { "alias": "rei" }
      }
    }
  }
}
```

Then restart: `clawdbot gateway restart`

## Troubleshooting

**403 errors:** The `User-Agent: Clawdbot/1.0` header is required. The setup script adds this automatically. If you configured manually, make sure the header is present.

**"Model not allowed":** Rei must be in `agents.defaults.models` to switch to it. The setup script handles this. For manual setup, add the allowlist entry shown above.
