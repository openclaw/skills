# Fliz API Reference

Complete technical documentation for all Fliz REST API endpoints.

## Base Configuration

```
Base URL: https://app.fliz.ai
Authentication: Bearer Token
Content-Type: application/json
```

## Authentication Header

```http
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

Obtain your token at: https://app.fliz.ai/api-keys

---

## Endpoints

### POST /api/rest/video

Create a new AI-generated video.

**Request Body:**
```json
{
  "fliz_video_create_input": {
    "name": "string (required) - Video title",
    "description": "string (required) - Full text content",
    "format": "size_16_9|size_9_16|square (required)",
    "lang": "string (required) - ISO 639-1 code",
    "category": "article|product|ad",
    "script_style": "string - Narrative style enum",
    "image_style": "string - Visual style enum",
    "image_urls": ["string"] - Required for product/ad (3-10 URLs),
    "caption_style": "animated_background|bouncing_background|colored_words|scaling_words",
    "caption_position": "bottom|center",
    "caption_font": "poppins|roboto|montserrat|...",
    "caption_color": "#FFFFFF - Hex color",
    "caption_uppercase": "boolean",
    "voice_id": "string - Custom voice ID",
    "is_male_voice": "boolean",
    "music_id": "string - From /api/rest/musics",
    "music_url": "string - Custom music URL",
    "music_volume": "integer 0-100",
    "watermark_url": "string - Image URL",
    "site_url": "string - CTA URL",
    "site_name": "string - CTA display text",
    "webhook_url": "string - Callback URL",
    "is_automatic": "boolean - Auto-process to completion",
    "video_animation_mode": "full_video|hook_only"
  }
}
```

**Response 200:**
```json
{
  "fliz_video_create": {
    "video_id": "uuid"
  }
}
```

**Errors:**
- 400: Invalid parameters
- 401: Invalid/expired token
- 429: Rate limit exceeded

---

### GET /api/rest/videos/{id}

Retrieve video details and status.

**Path Parameters:**
- `id` (required): UUID format `[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}`

**Response 200:**
```json
{
  "fliz_video_by_pk": {
    "id": "uuid",
    "title": "string",
    "category": "article|product|ad",
    "format": "size_16_9|size_9_16|square",
    "lang": "string",
    "step": "string - Processing step enum",
    "url": "string|null - MP4 URL when complete",
    "error": "object|null - Error details if failed",
    "created_at": "ISO 8601 timestamp",
    "voice_id": "string|null",
    "music": {
      "id": "uuid",
      "url": "string"
    },
    "watermark": {
      "id": "uuid",
      "url": "string"
    },
    "remotion_configuration": "object - Video config"
  }
}
```

**Processing Steps (step field):**
```
pending → scrapping → script → image_prompt → image_generation → 
image_analysis → speech → transcribe → video → video_rendering → 
video_rendering_queue → complete

Error states: failed, failed_unrecoverable, failed_go_back_to_user_action
Special: user_action (requires manual intervention), block
```

---

### GET /api/rest/videos

List all videos with pagination.

**Query Parameters:**
- `limit` (integer): Number of results (default: 20)
- `offset` (integer): Pagination offset (default: 0)

**Response 200:**
```json
{
  "fliz_video": [
    {
      "id": "uuid",
      "title": "string",
      "category": "string",
      "format": "string",
      "lang": "string",
      "step": "string",
      "url": "string|null",
      "error": "object|null",
      "created_at": "timestamp"
    }
  ]
}
```

---

### POST /api/rest/videos/{from_video_id}/translate

Translate an existing video to a new language.

**Path Parameters:**
- `from_video_id` (required): Source video UUID

**Query/Body Parameters:**
- `new_lang` (required): Target language ISO 639-1 code
- `is_automatic` (optional): Boolean
- `webhook_url` (optional): Callback URL

**Response 200:**
```json
{
  "fliz_video_translate": {
    "new_video_id": "uuid"
  }
}
```

---

### POST /api/rest/videos/{from_video_id}/duplicate

Create a copy of an existing video.

**Path Parameters:**
- `from_video_id` (required): Source video UUID

**Response 200:**
```json
{
  "fliz_video_duplicate": {
    "new_video_id": "uuid"
  }
}
```

---

### GET /api/rest/voices

List available text-to-speech voices.

**Response 200:**
```json
{
  "fliz_list_voices": {
    "voices": [
      {
        "id": "string - Voice ID to use in create_video",
        "name": "string - Display name",
        "gender": "male|female",
        "samples": ["string"] - Sample audio URLs
      }
    ]
  }
}
```

---

### GET /api/rest/musics

List available background music tracks.

**Response 200:**
```json
{
  "fliz_list_musics": {
    "musics": [
      {
        "id": "string - Music ID to use in create_video",
        "name": "string - Track name",
        "theme": "string - Category (ambient, upbeat, etc.)",
        "url": "string - Preview URL"
      }
    ]
  }
}
```

---

## Webhook Payload

When `webhook_url` is configured, Fliz sends POST requests on video completion or failure:

**Success:**
```json
{
  "event": "video.complete",
  "video_id": "uuid",
  "step": "complete",
  "url": "https://cdn.fliz.ai/videos/xxx.mp4",
  "title": "string",
  "format": "string",
  "lang": "string"
}
```

**Error:**
```json
{
  "event": "video.failed",
  "video_id": "uuid",
  "step": "failed|failed_unrecoverable",
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

---

## Rate Limits

- Respect 429 responses with exponential backoff
- Recommended: 1 request/second for polling
- Polling interval: 10-30 seconds for status checks

## UUID Format

All video IDs follow UUID v4 pattern:
```regex
[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}
```

Example: `a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d`

## Language Codes (ISO 639-1)

Common codes: `en`, `fr`, `es`, `de`, `it`, `pt`, `nl`, `pl`, `ru`, `ja`, `ko`, `zh`, `ar`, `hi`
