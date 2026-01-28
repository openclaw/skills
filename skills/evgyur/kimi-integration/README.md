# Kimi Integration for Clawdbot

Complete integration guide for adding Moonshot AI (Kimi K2.5) and Kimi Code models to Clawdbot.

## Overview

This skill provides step-by-step instructions for integrating two Kimi model families:

- **Moonshot AI (Kimi K2.5)** - General-purpose models with 200K context window
- **Kimi Code** - Specialized coding model optimized for programming tasks

Both providers use separate API keys and endpoints.

## Installation

```bash
clawdbot skills install kimi-integration.skill
```

Or manually install by placing the skill folder in your Clawdbot skills directory.

## Quick Start

### 1. Get API Keys

- **Moonshot AI**: https://platform.moonshot.cn
- **Kimi Code**: https://api.kimi.com/coding

### 2. Set Environment Variables

```bash
export MOONSHOT_API_KEY="sk-your-moonshot-key"
export KIMICODE_API_KEY="sk-your-kimicode-key"
```

### 3. Configure Clawdbot

Add to your `clawdbot.json`:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "moonshot/kimi-k2.5"
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "moonshot": {
        "baseUrl": "https://api.moonshot.cn/v1",
        "apiKey": "${MOONSHOT_API_KEY}",
        "api": "openai-completions",
        "models": [
          { "id": "kimi-k2.5", "name": "Kimi K2.5", "contextWindow": 200000 }
        ]
      }
    }
  }
}
```

### 4. Restart and Verify

```bash
clawdbot gateway restart
clawdbot models list
```

## Features

- ✅ Complete configuration examples for both providers
- ✅ Multi-model setup with failover support
- ✅ Model aliases for quick switching
- ✅ API connection test script
- ✅ Troubleshooting guide
- ✅ Cost and context window specifications

## Available Models

### Moonshot AI

| Model | Context Window | Max Output | Use Case |
|-------|----------------|------------|----------|
| `kimi-k2.5` | 200K | 8K | General purpose, large context |
| `moonshot-v1-128k` | 128K | 16K | Legacy model |
| `moonshot-v1-32k` | 32K | 8K | Standard tasks |
| `moonshot-v1-8k` | 8K | 2K | Quick responses |

### Kimi Code

| Model | Context Window | Max Output | Use Case |
|-------|----------------|------------|----------|
| `kimi-for-coding` | 200K | 8K | Code generation & analysis |

## Usage Examples

### Switch models in chat

```bash
/model moonshot/kimi-k2.5
/model kimicode/kimi-for-coding
```

### Use model aliases

```bash
/model k25    # Kimi K2.5
/model kimi   # Kimi for Coding
```

### Set as default

```bash
clawdbot models set moonshot/kimi-k2.5
```

## Testing

Run the connection test script:

```bash
bash scripts/test_kimi_connection.sh
```

This verifies:
- API keys are set correctly
- Endpoints are accessible
- Authentication works

## Documentation

- **SKILL.md** - Complete integration guide with step-by-step instructions
- **references/config-examples.md** - Ready-to-use configuration snippets
- **scripts/test_kimi_connection.sh** - API connection tester

## Troubleshooting

### Models not showing in list

```bash
# Check config syntax
clawdbot gateway config.get | grep -A 20 moonshot

# Verify API keys
echo $MOONSHOT_API_KEY
echo $KIMICODE_API_KEY
```

### Authentication errors

- Ensure API key starts with `sk-`
- Verify key is valid on provider dashboard
- Check correct base URL for each provider

### Connection issues

Test endpoint directly:

```bash
curl -X POST "https://api.moonshot.cn/v1/chat/completions" \
  -H "Authorization: Bearer $MOONSHOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "kimi-k2.5", "messages": [{"role": "user", "content": "test"}]}'
```

## Resources

- [Moonshot AI Documentation](https://platform.moonshot.cn/docs)
- [Kimi Code API](https://api.kimi.com/coding/docs)
- [Clawdbot Model Providers](https://docs.clawd.bot/concepts/model-providers)

## Contributing

Found an issue or have suggestions? Open an issue or submit a pull request!

## License

MIT
