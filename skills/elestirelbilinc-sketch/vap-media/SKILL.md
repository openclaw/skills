---
name: vap-media
description: AI image, video, and music generation. Flux, Veo 3.1, Suno V5.
homepage: https://vapagent.com
metadata: {"clawdbot":{"emoji":"🎬","requires":{"bins":["curl"],"env":["VAP_API_KEY"]},"primaryEnv":"VAP_API_KEY"}}
---

# VAP Media Generation

Generate AI images, videos, and music directly via the VAP API. No local dependencies beyond `curl`.

## Available Models

| Type | Model | Use Case |
|------|-------|----------|
| Image | Flux | Social posts, product mockups |
| Video | Veo 3.1 | Clips, promos, content |
| Music | Suno V5 | Background tracks, jingles |

## Quick Usage

### Generate an Image

```bash
curl -s -X POST https://api.vapagent.com/v3/tasks \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "image_generation",
    "params": {
      "description": "A serene mountain landscape at golden hour",
      "aspect_ratio": "16:9"
    }
  }' | jq -r '.task_id'
```

### Check Status & Get Result

```bash
curl -s https://api.vapagent.com/v3/tasks/{task_id} \
  -H "Authorization: Bearer $VAP_API_KEY" | jq '.status, .result.url'
```

### Generate Video (Tier 2+ required)

```bash
curl -s -X POST https://api.vapagent.com/v3/tasks \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "video_generation",
    "params": {
      "prompt": "Cinematic aerial shot of coastal cliffs",
      "duration": 8,
      "aspect_ratio": "16:9"
    }
  }'
```

### Generate Music (Tier 2+ required)

```bash
curl -s -X POST https://api.vapagent.com/v3/tasks \
  -H "Authorization: Bearer $VAP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "music_generation",
    "params": {
      "prompt": "Upbeat indie folk with acoustic guitar",
      "duration": 120,
      "instrumental": false
    }
  }'
```

## Setup

1. **Get API Key:** https://vapagent.com/dashboard/signup.html
2. **Add to environment:**
   ```bash
   export VAP_API_KEY=vape_xxxxxxxxxxxxxxxxxxxx
   ```
3. **Or configure in clawdbot.json:**
   ```json
   {
     "skills": {
       "entries": {
         "vap-media": {
           "apiKey": "vape_xxxxxxxxxxxxxxxxxxxx"
         }
       }
     }
   }
   ```

## Tier System

| Tier | Requirement | Capabilities |
|------|-------------|--------------|
| Tier 1 | $1+ deposit | Image only |
| Tier 2 | $100+ deposit, 50+ tasks | Image + Video + Music |

## Cost Control

VAP uses **reserve-burn-refund** billing:

- **Reserve:** Cost is held before execution
- **Burn:** Only charged on success
- **Refund:** Failed tasks are automatically refunded

No surprise charges. You know exact cost before execution.

## Response Format

```json
{
  "task_id": "tsk_abc123",
  "status": "completed",
  "result": {
    "url": "https://pub-xxx.r2.dev/output.png",
    "metadata": {}
  }
}
```

## Example Workflows

### Daily Social Post
"Generate an inspirational quote image with abstract background" → Post to social media

### Product Mockup
"Product photo of a minimalist coffee mug on marble surface" → Use for e-commerce

### Content Background Music
"Calm lo-fi beats for focus and productivity" → Add to video content

## Links

- [API Documentation](https://api.vapagent.com/docs)
- [Quick Start Guide](https://vapagent.com/quick-start.html)
- [MCP Integration](https://registry.modelcontextprotocol.io)
- [GitHub](https://github.com/vapagentmedia/vap-showcase)

## Support

- Email: support@vapagent.com
- Issues: https://github.com/vapagentmedia/vap-showcase/issues
