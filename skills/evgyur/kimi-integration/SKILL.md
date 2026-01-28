---
name: kimi-integration
description: Step-by-step guide for integrating Moonshot AI (Kimi) and Kimi Code models into Clawdbot. Use when someone asks how to add Kimi models, configure Moonshot AI, or set up Kimi for Coding in Clawdbot.
---

# Kimi Model Integration

Complete guide for adding Moonshot AI (Kimi) and Kimi Code models to Clawdbot.

## Overview

Kimi offers two separate model families:

1. **Moonshot AI (Kimi K2)** - General-purpose models via OpenAI-compatible API
2. **Kimi Code** - Specialized coding model with dedicated endpoint

Both require API keys from different sources.

## Prerequisites

- Clawdbot installed and configured
- API keys (see Getting API Keys section)

## Getting API Keys

### Moonshot AI (Kimi K2)

1. Visit https://platform.moonshot.cn
2. Register an account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-...`)

### Kimi Code

1. Visit https://api.kimi.com/coding
2. Register an account  
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key (starts with `sk-...`)

**Note:** Moonshot and Kimi Code use separate keys and endpoints.

## Integration Steps

### Option 1: Moonshot AI (Kimi K2 models)

#### Step 1: Set environment variable

```bash
export MOONSHOT_API_KEY="sk-your-moonshot-key-here"
```

Or add to `.env` file:

```bash
echo 'MOONSHOT_API_KEY="sk-your-moonshot-key-here"' >> ~/.env
```

#### Step 2: Add provider configuration

Edit your `clawdbot.json` config:

```json5
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
          {
            "id": "moonlight-v1-32k",
            "name": "Moonlight V1 32K",
            "contextWindow": 32768
          },
          {
            "id": "moonshot-v1-8k",
            "name": "Moonshot V1 8K",
            "contextWindow": 8192
          },
          {
            "id": "moonshot-v1-32k",
            "name": "Moonshot V1 32K",
            "contextWindow": 32768
          },
          {
            "id": "moonshot-v1-128k",
            "name": "Moonshot V1 128K",
            "contextWindow": 131072
          },
          {
            "id": "kimi-k2.5",
            "name": "Kimi K2.5",
            "contextWindow": 200000
          }
        ]
      }
    }
  }
}
```

#### Step 3: Restart Clawdbot

```bash
clawdbot gateway restart
```

#### Step 4: Verify integration

```bash
clawdbot models list
```

You should see Moonshot models in the list.

#### Step 5: Use the model

Set as default:
```bash
clawdbot models set moonshot/kimi-k2.5
```

Or use model aliases in chat:
```bash
/model moonshot/kimi-k2.5
```

### Option 2: Kimi Code (specialized coding model)

#### Step 1: Set environment variable

```bash
export KIMICODE_API_KEY="sk-your-kimicode-key-here"
```

Or add to `.env`:

```bash
echo 'KIMICODE_API_KEY="sk-your-kimicode-key-here"' >> ~/.env
```

#### Step 2: Add provider configuration

Edit your `clawdbot.json` config:

```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "kimicode/kimi-for-coding"
      },
      "models": {
        "kimicode/kimi-for-coding": {
          "alias": "kimi"
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
            "maxTokens": 8192
          }
        ]
      }
    }
  }
}
```

#### Step 3: Restart Clawdbot

```bash
clawdbot gateway restart
```

#### Step 4: Verify integration

```bash
clawdbot models list
```

You should see `kimicode/kimi-for-coding` in the list.

#### Step 5: Use the model

Set as default:
```bash
clawdbot models set kimicode/kimi-for-coding
```

Or use model alias in chat:
```bash
/model kimi
```

## Using Both Providers

You can configure both Moonshot and Kimi Code simultaneously:

```json5
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "moonshot/kimi-k2.5"
      },
      "models": {
        "kimicode/kimi-for-coding": {
          "alias": "kimi"
        },
        "moonshot/kimi-k2.5": {
          "alias": "k25"
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

Switch between models using aliases:
- `/model k25` - Kimi K2.5 (general)
- `/model kimi` - Kimi for Coding (specialized)

## Troubleshooting

### Model not appearing in list

Check config syntax:
```bash
clawdbot gateway config.get | grep -A 20 moonshot
```

Verify API key is set:
```bash
echo $MOONSHOT_API_KEY
echo $KIMICODE_API_KEY
```

### Authentication errors

- Verify API key starts with `sk-`
- Check key is valid on provider dashboard
- Ensure correct base URL for each provider

### Connection issues

Test API endpoint directly:
```bash
curl -X POST "https://api.moonshot.cn/v1/chat/completions" \
  -H "Authorization: Bearer $MOONSHOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "kimi-k2.5", "messages": [{"role": "user", "content": "test"}]}'
```

## Model Recommendations

- **Kimi K2.5** (`moonshot/kimi-k2.5`) - Best for general tasks, 200K context
- **Kimi for Coding** (`kimicode/kimi-for-coding`) - Specialized for code generation
- **Moonshot V1 128K** (`moonshot/moonshot-v1-128k`) - Legacy model, 128K context

## References

- Moonshot AI Docs: https://platform.moonshot.cn/docs
- Kimi Code API: https://api.kimi.com/coding/docs
- Clawdbot Model Providers: /home/eyurc/clawdbot/docs/concepts/model-providers.md
