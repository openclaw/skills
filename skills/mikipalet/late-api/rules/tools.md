# Tools API

Media download and utility tools. Available to paid plans only.

**Rate limits:** Build (50/day), Accelerate (500/day), Unlimited (unlimited)

## Download Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/v1/tools/instagram/download` | Download Instagram media |
| `GET` | `/v1/tools/tiktok/download` | Download TikTok video |
| `GET` | `/v1/tools/twitter/download` | Download Twitter media |
| `GET` | `/v1/tools/youtube/download` | Download YouTube video |
| `GET` | `/v1/tools/linkedin/download` | Download LinkedIn media |
| `GET` | `/v1/tools/facebook/download` | Download Facebook media |
| `GET` | `/v1/tools/bluesky/download` | Download Bluesky media |

## Download Example

```bash
curl "https://getlate.dev/api/v1/tools/instagram/download?url=https://www.instagram.com/p/ABC123/" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Response:

```json
{
  "success": true,
  "downloadUrl": "https://storage.getlate.dev/downloads/abc123.mp4"
}
```

## Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/tools/instagram/hashtag-checker` | Check hashtag restrictions |
| `GET` | `/v1/tools/youtube/transcript` | Get YouTube video transcript |

## Hashtag Checker

```bash
curl -X POST https://getlate.dev/api/v1/tools/instagram/hashtag-checker \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"hashtags": ["travel", "photography", "banned123"]}'
```

Response:

```json
{
  "results": [
    { "hashtag": "travel", "status": "safe" },
    { "hashtag": "photography", "status": "safe" },
    { "hashtag": "banned123", "status": "restricted", "reason": "Community guidelines" }
  ]
}
```

Status values: `safe`, `restricted`, `banned`, `unknown`

## YouTube Transcript

```bash
curl "https://getlate.dev/api/v1/tools/youtube/transcript?url=https://youtube.com/watch?v=dQw4w9WgXcQ" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

Returns timestamped transcript of the video.
