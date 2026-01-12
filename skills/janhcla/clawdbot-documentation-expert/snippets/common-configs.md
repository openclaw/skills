# Common Clawdbot Configuration Snippets

Quick-reference config patterns extracted from documentation.

## Discord Setup

### Basic Discord Bot
```json
{
  "discord": {
    "botToken": "YOUR_BOT_TOKEN",
    "guilds": {
      "*": {
        "requireMention": true
      }
    }
  }
}
```

### Discord with Specific Channels
```json
{
  "discord": {
    "botToken": "YOUR_BOT_TOKEN",
    "guilds": {
      "GUILD_ID": {
        "channels": {
          "CHANNEL_ID": { "enabled": true }
        },
        "requireMention": true
      }
    }
  }
}
```

## Telegram Setup

```json
{
  "telegram": {
    "botToken": "YOUR_BOT_TOKEN",
    "allowedUsers": ["username1", "username2"]
  }
}
```

## WhatsApp Setup

```json
{
  "whatsapp": {
    "enabled": true
  }
}
```
Then run: `clawdbot login` to scan QR code.

## Signal Setup

```json
{
  "signal": {
    "number": "+1234567890",
    "allowedNumbers": ["+1987654321"]
  }
}
```

## Gateway Configuration

### Local Only (default)
```json
{
  "gateway": {
    "mode": "local",
    "bind": "loopback",
    "port": 18789
  }
}
```

### With Tailscale
```json
{
  "gateway": {
    "mode": "local",
    "tailscale": {
      "mode": "serve",
      "resetOnExit": true
    }
  }
}
```

## Agent Defaults

```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-sonnet-4-5",
      "userTimezone": "America/New_York"
    }
  }
}
```

## Message Settings

```json
{
  "messages": {
    "ackReaction": "👀",
    "textChunkLimit": 1900,
    "historyLimit": 20,
    "replyToMode": "first"
  }
}
```

## Retry Configuration

```json
{
  "retry": {
    "attempts": 2,
    "minDelayMs": 2000,
    "maxDelayMs": 60000,
    "jitter": 0.2
  }
}
```

## Cron Jobs

```json
{
  "cron": {
    "jobs": [
      {
        "id": "morning-check",
        "schedule": "0 9 * * *",
        "message": "Good morning! What's on the agenda today?",
        "enabled": true
      }
    ]
  }
}
```

## Skills Configuration

```json
{
  "skills": {
    "directories": ["./skills", "~/my-skills"],
    "entries": {
      "my-skill": {
        "apiKey": "xxx"
      }
    }
  }
}
```

## Model Overrides

```json
{
  "models": {
    "aliases": {
      "fast": "anthropic/claude-sonnet-4-5",
      "smart": "anthropic/claude-opus-4-5"
    },
    "failover": {
      "enabled": true,
      "fallbacks": ["openai/gpt-4o"]
    }
  }
}
```

## Heartbeat

```json
{
  "heartbeat": {
    "enabled": true,
    "intervalMinutes": 30
  }
}
```

---

*These snippets are starting points - see full docs for all options.*
