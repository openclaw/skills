# Configuration Examples

Complete configuration examples for different Kimi integration scenarios.

## Minimal Moonshot Configuration

```json5
{
  "models": {
    "mode": "merge",
    "providers": {
      "moonshot": {
        "baseUrl": "https://api.moonshot.cn/v1",
        "apiKey": "${MOONSHOT_API_KEY}",
        "api": "openai-completions",
        "models": [
          { "id": "kimi-k2.5", "name": "Kimi K2.5" }
        ]
      }
    }
  }
}
```

## Full Moonshot Model Catalog

```json5
{
  "models": {
    "mode": "merge",
    "providers": {
      "moonshot": {
        "baseUrl": "https://api.moonshot.cn/v1",
        "apiKey": "${MOONSHOT_API_KEY}",
        "api": "openai-completions",
        "models": [
          {
            "id": "moonlight-v1-32k",
            "name": "Moonlight V1 32K",
            "contextWindow": 32768,
            "maxTokens": 8192,
            "cost": {
              "input": 0.00001,
              "output": 0.00001,
              "cacheRead": 0,
              "cacheWrite": 0
            }
          },
          {
            "id": "moonshot-v1-8k",
            "name": "Moonshot V1 8K",
            "contextWindow": 8192,
            "maxTokens": 2048,
            "cost": {
              "input": 0.000012,
              "output": 0.000012,
              "cacheRead": 0,
              "cacheWrite": 0
            }
          },
          {
            "id": "moonshot-v1-32k",
            "name": "Moonshot V1 32K",
            "contextWindow": 32768,
            "maxTokens": 8192,
            "cost": {
              "input": 0.000024,
              "output": 0.000024,
              "cacheRead": 0,
              "cacheWrite": 0
            }
          },
          {
            "id": "moonshot-v1-128k",
            "name": "Moonshot V1 128K",
            "contextWindow": 131072,
            "maxTokens": 16384,
            "cost": {
              "input": 0.000060,
              "output": 0.000060,
              "cacheRead": 0,
              "cacheWrite": 0
            }
          },
          {
            "id": "kimi-k2.5",
            "name": "Kimi K2.5",
            "contextWindow": 200000,
            "maxTokens": 8192,
            "cost": {
              "input": 0.000001,
              "output": 0.000001,
              "cacheRead": 0,
              "cacheWrite": 0
            }
          }
        ]
      }
    }
  }
}
```

## Kimi Code with Aliases

```json5
{
  "agents": {
    "defaults": {
      "models": {
        "kimicode/kimi-for-coding": {
          "alias": "kimi",
          "description": "Specialized coding model"
        }
      }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "kimicode": {
        "baseUrl": "https://api.kimi.com/coding/v1",
        "apiKey": "${KIMICODE_API_KEY}",
        "api": "openai-completions",
        "models": [
          {
            "id": "kimi-for-coding",
            "name": "Kimi For Coding",
            "contextWindow": 200000,
            "maxTokens": 8192,
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            }
          }
        ]
      }
    }
  }
}
```

## Multi-Model Setup with Failover

```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "moonshot/kimi-k2.5",
        "fallback": [
          "kimicode/kimi-for-coding",
          "anthropic/claude-sonnet-4-5"
        ]
      },
      "models": {
        "moonshot/kimi-k2.5": {
          "alias": "k25"
        },
        "kimicode/kimi-for-coding": {
          "alias": "kimi"
        }
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
      },
      "kimicode": {
        "baseUrl": "https://api.kimi.com/coding/v1",
        "apiKey": "${KIMICODE_API_KEY}",
        "api": "openai-completions",
        "models": [
          { "id": "kimi-for-coding", "name": "Kimi For Coding", "contextWindow": 200000 }
        ]
      }
    }
  }
}
```

## Environment Variables Setup

### Using .env file

Create or edit `~/.env`:

```bash
# Moonshot AI (Kimi K2.5)
MOONSHOT_API_KEY="sk-your-moonshot-key-here"

# Kimi Code
KIMICODE_API_KEY="sk-your-kimicode-key-here"
```

### Using shell exports

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export MOONSHOT_API_KEY="sk-your-moonshot-key-here"
export KIMICODE_API_KEY="sk-your-kimicode-key-here"
```

Then reload:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Using Clawdbot config directly

```json5
{
  "env": {
    "MOONSHOT_API_KEY": "sk-your-moonshot-key-here",
    "KIMICODE_API_KEY": "sk-your-kimicode-key-here"
  },
  "models": {
    "mode": "merge",
    "providers": {
      "moonshot": {
        "baseUrl": "https://api.moonshot.cn/v1",
        "apiKey": "${MOONSHOT_API_KEY}",
        "api": "openai-completions",
        "models": [
          { "id": "kimi-k2.5", "name": "Kimi K2.5" }
        ]
      }
    }
  }
}
```

**Note:** Storing keys directly in config is less secure. Prefer environment variables or `.env` file.

## Testing Configuration

### Verify config syntax

```bash
clawdbot gateway config.get
```

### List available models

```bash
clawdbot models list
```

### Test API connection

```bash
curl -X POST "https://api.moonshot.cn/v1/chat/completions" \
  -H "Authorization: Bearer $MOONSHOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "kimi-k2.5",
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "max_tokens": 100
  }'
```

### Switch model in chat

```
/model moonshot/kimi-k2.5
```

Or use alias:
```
/model k25
```
