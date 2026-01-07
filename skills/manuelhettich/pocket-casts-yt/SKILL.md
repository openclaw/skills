---
name: pocket-casts
description: Download YouTube videos and upload them to Pocket Casts Files for offline viewing. For personal use with content you own or have rights to.
version: 1.0.0
author: emmanuelem
---

# Pocket Casts YouTube Uploader

Download YouTube videos and upload them to Pocket Casts Files for offline viewing.

## Usage

```bash
~/skills/pocket-casts/scripts/upload.sh "YOUTUBE_URL"
```

Or with a custom title:
```bash
~/skills/pocket-casts/scripts/upload.sh "YOUTUBE_URL" "Custom Title"
```

## Prerequisites

### Required
- **yt-dlp** - YouTube downloader (via uv: `uvx yt-dlp`)
- **ffmpeg** - Video processing (`apt install ffmpeg`)
- **curl** - HTTP requests (usually pre-installed)
- **jq** - JSON parsing (`apt install jq`)

### Recommended  
- **deno** - JavaScript runtime for yt-dlp challenges:
  ```bash
  curl -fsSL https://deno.land/install.sh | sh
  ```
  Add to PATH: `export PATH="$HOME/.deno/bin:$PATH"`

## Setup

1. **Create credentials directory:**
   ```bash
   mkdir -p ~/.clawdbot/credentials/pocket-casts
   chmod 700 ~/.clawdbot/credentials/pocket-casts
   ```

2. **Add Pocket Casts refresh token:**
   
   Get your refresh token from browser dev tools while logged into pocketcasts.com, then:
   ```bash
   cat > ~/.clawdbot/credentials/pocket-casts/config.json << 'EOF'
   {
     "refreshToken": "YOUR_REFRESH_TOKEN_HERE"
   }
   EOF
   chmod 600 ~/.clawdbot/credentials/pocket-casts/config.json
   ```
   
   The refresh token lasts ~1 year. Access tokens are fetched automatically.

3. **Add YouTube cookies** (required for most videos):
   
   YouTube's bot detection requires cookies from a logged-in browser session.
   
   - Install "Get cookies.txt LOCALLY" browser extension (or similar)
   - Go to youtube.com while logged in
   - Export cookies via the extension
   - Save to `~/.clawdbot/credentials/pocket-casts/cookies.txt`
   
   ```bash
   chmod 600 ~/.clawdbot/credentials/pocket-casts/cookies.txt
   ```

## How It Works

1. Downloads video via `yt-dlp --remux-video mp4`
2. Refreshes Pocket Casts access token using stored refresh token
3. Requests presigned upload URL from Pocket Casts API
4. PUTs file to S3 via presigned URL
5. Deletes local video file

## Environment Variables

- `CLAWDBOT_CREDENTIALS` - Override credentials directory (default: `~/.clawdbot/credentials`)

## Notes

- Files appear in the Pocket Casts "Files" tab
- Videos play natively in the app (iOS/Android/Web)
- Max file size depends on your Pocket Casts subscription (~2GB for Plus)
- Cookies may need refreshing if YouTube blocks requests

## ⚠️ Legal Disclaimer

**This skill is provided for personal, fair-use purposes only.**

- **YouTube Terms of Service** prohibit downloading videos except via official means. Downloading may violate YouTube's ToS depending on your jurisdiction and intended use.
- **Pocket Casts Terms** require that you own or have the rights to any media you upload to your Files library.
- **Copyright law** varies by country. Downloading and storing copyrighted content without permission may be illegal in your jurisdiction.

By using this skill, you accept full responsibility for ensuring your use complies with all applicable terms of service and laws. The authors disclaim any liability for misuse.

**Recommended uses:** Personal recordings, Creative Commons content, videos you created, or content where the creator has explicitly permitted downloading.
