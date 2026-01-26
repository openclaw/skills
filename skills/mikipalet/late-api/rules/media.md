# Media Upload

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/media/presign` | Get presigned upload URL |

## Get Presigned URL

```bash
curl -X POST https://getlate.dev/api/v1/media/presign \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filename": "image.jpg", "contentType": "image/jpeg"}'
```

## Upload Flow

```typescript
// 1. Get presigned URL
const { uploadUrl, fileUrl } = await getPresignedUrl('image.jpg', 'image/jpeg');

// 2. Upload to presigned URL
await fetch(uploadUrl, {
  method: 'PUT',
  body: fileBuffer,
  headers: { 'Content-Type': 'image/jpeg' }
});

// 3. Use fileUrl in post
await createPost({
  content: 'Check this out!',
  mediaItems: [{ type: 'image', url: fileUrl }],
  platforms: [{ platform: 'twitter', accountId: 'acc_123' }]
});
```

## Supported Formats

| Type | Formats | Max Size |
|------|---------|----------|
| Images | JPG, PNG, WebP, GIF | 5MB |
| Videos | MP4, MOV, WebM | 5GB |
| Documents | PDF (LinkedIn only) | 100MB |

## Platform Media Limits

| Platform | Max Images | Max Video | Special |
|----------|-----------|-----------|---------|
| Instagram | 8MB | 100MB stories, 300MB reels | 4:5 to 1.91:1 aspect |
| TikTok | 20MB | 4GB, 10min max | 9:16 strict |
| Twitter | 5MB | 512MB, 2min 20s | 1-4 images |
| LinkedIn | 8MB | 5GB | 20 image carousel |
| YouTube | 2MB thumbnail | 256GB | Resumable upload |
| Facebook | 10MB | 4GB | 10 multi-image |
| Threads | 8MB | 1GB, 5min | 10 carousel |
| Pinterest | 32MB | 2GB | Requires cover image |
| Bluesky | 1MB | 50MB, 3min | 4 images max |
| Snapchat | 20MB | 500MB | AES encryption required |
| Google Business | 5MB | N/A | Images only |
| Reddit | 20MB | N/A | Via URL |
| Telegram | 10MB | 50MB | 4096 char limit |
