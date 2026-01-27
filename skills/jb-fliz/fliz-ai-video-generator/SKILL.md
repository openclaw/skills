---
name: fliz-ai-video-generator
version: 1.0.0
author: gregorybeyrouti
description: |
  Complete integration guide for the Fliz REST API - an AI-powered video generation platform that transforms text content into professional videos with voiceovers, AI-generated images, and subtitles.
  
  Use this skill when:
  - Creating integrations with Fliz API (WordPress, Zapier, Make, n8n, custom apps)
  - Building video generation workflows via API
  - Implementing webhook handlers for video completion notifications
  - Developing automation tools that create, manage, or translate videos
  - Troubleshooting Fliz API errors or authentication issues
  - Understanding video processing steps and status polling
  
  Key capabilities: video creation from text/Brief, video status monitoring, translation, duplication, voice/music listing, webhook notifications.
homepage: https://fliz.ai
tags: [video, ai, fliz, content-creation, automation, api]
metadata:
  clawdbot:
    emoji: "🎬"
    primaryEnv: FLIZ_API_KEY
---

# Fliz API Integration Skill

Transform text content into AI-generated videos programmatically.

## Quick Reference

| Item | Value |
|------|-------|
| Base URL | `https://app.fliz.ai` |
| Auth | Bearer Token (JWT) |
| Get Token | https://app.fliz.ai/api-keys |
| API Docs | https://app.fliz.ai/api-docs |
| Format | JSON |

## Authentication

All requests require Bearer token authentication:

```bash
curl -X GET "https://app.fliz.ai/api/rest/voices" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"
```

Test connection by calling `GET /api/rest/voices` - returns 200 if token is valid.

## Core Endpoints

### 1. Create Video

```
POST /api/rest/video
```

**Minimal request:**
```json
{
  "fliz_video_create_input": {
    "name": "Video Title",
    "description": "Full content text to transform into video",
    "format": "size_16_9",
    "lang": "en"
  }
}
```

**Response:**
```json
{
  "fliz_video_create": {
    "video_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
  }
}
```

> **CRITICAL**: The `description` field must contain the FULL TEXT content. Fliz does NOT extract content from URLs - upstream systems must fetch/process content first.

### 2. Get Video Status

```
GET /api/rest/videos/{id}
```

Poll this endpoint to track video generation progress. Check the `step` field:

| Step | Status |
|------|--------|
| `pending` → `scrapping` → `script` → `image_*` → `speech` → `video_rendering` | Processing |
| `complete` | ✅ Ready - `url` field contains MP4 |
| `failed` / `failed_unrecoverable` | ❌ Error - check `error` field |
| `user_action` | ⚠️ Requires manual intervention |

### 3. List Videos

```
GET /api/rest/videos?limit=20&offset=0
```

### 4. Translate Video

```
POST /api/rest/videos/{from_video_id}/translate?new_lang=fr
```

Creates a new video in the target language.

### 5. Duplicate Video

```
POST /api/rest/videos/{from_video_id}/duplicate
```

### 6. List Voices / Musics

```
GET /api/rest/voices
GET /api/rest/musics
```

## Video Creation Parameters

### Required Fields
- `name` (string): Video title
- `description` (string): Full text content
- `format` (enum): `size_16_9` | `size_9_16` | `square`
- `lang` (string): ISO 639-1 code (en, fr, es, de, pt, etc.)

### Optional Customization

| Field | Description | Default |
|-------|-------------|---------|
| `category` | `article` \| `product` \| `ad` | `article` |
| `script_style` | Narrative style | auto |
| `image_style` | Visual style | `hyperrealistic` |
| `caption_style` | Subtitle style | `animated_background` |
| `caption_position` | `bottom` \| `center` | `bottom` |
| `caption_font` | Font family | `poppins` |
| `caption_color` | Hex color (#FFFFFF) | white |
| `caption_uppercase` | Boolean | false |
| `voice_id` | Custom voice ID | auto |
| `is_male_voice` | Boolean | auto |
| `music_id` | Music track ID | auto |
| `music_url` | Custom music URL | null |
| `music_volume` | 0-100 | 15 |
| `watermark_url` | Image URL | null |
| `site_url` | CTA URL | null |
| `site_name` | CTA text | null |
| `webhook_url` | Callback URL | null |
| `is_automatic` | Auto-process | true |
| `video_animation_mode` | `full_video` \| `hook_only` | `full_video` |
| `image_urls` | Array of URLs | null |

> **Note**: For `product` and `ad` categories, `image_urls` is required (3-10 images).

For complete enum values, see [references/enums-values.md](references/enums-values.md).

## Webhooks

Configure `webhook_url` to receive notifications when video is ready or fails:

```json
{
  "event": "video.complete",
  "video_id": "a1b2c3d4-...",
  "step": "complete",
  "url": "https://cdn.fliz.ai/videos/xxx.mp4"
}
```

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 200 | Success | Continue |
| 400 | Bad Request | Check params |
| 401 | Unauthorized | Invalid/expired token |
| 404 | Not Found | Invalid video ID |
| 429 | Rate Limited | Retry with backoff |
| 500 | Server Error | Retry later |

## Integration Patterns

### Polling Pattern (Recommended)
```
1. POST /api/rest/video → get video_id
2. Loop: GET /api/rest/videos/{id}
   - If step == "complete": done, get url
   - If step contains "failed": error
   - Else: wait 10-30s, retry
```

### Webhook Pattern
```
1. POST /api/rest/video with webhook_url
2. Process webhook callback when received
```

## Code Examples

See [assets/examples/](assets/examples/) for ready-to-use implementations:
- `python_client.py` - Full Python wrapper
- `nodejs_client.js` - Node.js implementation
- `curl_examples.sh` - cURL commands
- `webhook_handler.py` - Flask webhook server

## Scripts

| Script | Usage |
|--------|-------|
| `scripts/test_connection.py` | Validate API key |
| `scripts/create_video.py` | Create video from text file |
| `scripts/poll_status.py` | Monitor video generation |
| `scripts/list_resources.py` | Fetch voices/musics |

Run with: `python scripts/<script>.py --api-key YOUR_KEY`

## Common Issues

**"Invalid API response"**: Verify JSON structure matches documentation exactly.

**Video stuck in processing**: Check `step` field - some steps like `user_action` require manual intervention in Fliz dashboard.

**No URL extraction**: The API requires direct text input. Build content extraction into your integration.

## References

- [API Reference](references/api-reference.md) - Complete endpoint documentation
- [Enum Values](references/enums-values.md) - All valid parameter values
- [Integration Examples](assets/examples/) - Ready-to-use code
