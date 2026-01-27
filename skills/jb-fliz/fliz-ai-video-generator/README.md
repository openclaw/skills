# 🎬 Fliz AI Video Generator — Agent Skill

Generate AI-powered videos from text using the [Fliz](https://fliz.ai) API. Works with **Claude Code**, **Clawdbot**, and any AI agent that supports SKILL.md.

## What is Fliz?

Fliz transforms text content into professional videos with AI-generated voiceovers, images, and subtitles. Perfect for:
- 📰 Turning articles into video content
- 🛒 Creating product showcase videos
- 📱 Generating social media shorts (TikTok, Reels, YouTube Shorts)
- 🌍 Translating videos into 15+ languages

## Quick Start

### 1. Get your API key
Sign up at [fliz.ai](https://fliz.ai) and get your key at [app.fliz.ai/api-keys](https://app.fliz.ai/api-keys).

### 2. Install the skill

**Clawdbot:**
```bash
clawdhub install fliz-ai-video-generator
```

**Claude Code:**
Copy the `SKILL.md` file into your project's `.claude/skills/` directory.

### 3. Set your API key

```bash
export FLIZ_API_KEY="your-key-here"
```

### 4. Create a video

```bash
python scripts/create_video.py --name "My Video" --description "Your content here..." --lang fr --format size_9_16
```

## Features

| Feature | Description |
|---------|-------------|
| 🎥 Video Creation | Text → AI video with voiceover, images & subtitles |
| 🌍 Translation | Translate videos into 15+ languages |
| 🎨 68 Image Styles | From hyperrealistic to anime, pixel art, watercolor... |
| 📝 16 Script Styles | News, tutorial, podcast, e-commerce, children's story... |
| 🎵 Custom Music | Choose from library or use your own |
| 🔊 Custom Voices | Male/female, multiple languages |
| 📐 3 Formats | 16:9 (YouTube), 9:16 (TikTok/Reels), 1:1 (Instagram) |
| 🔗 Webhooks | Get notified when your video is ready |

## File Structure

```
fliz-ai-video-generator/
├── SKILL.md                    # Agent skill definition (for AI agents)
├── README.md                   # This file (for humans)
├── LICENSE.txt                 # MIT License
├── references/
│   ├── api-reference.md        # Complete API documentation
│   └── enums-values.md         # All valid parameter values
├── scripts/
│   ├── create_video.py         # Create a video from text
│   ├── poll_status.py          # Monitor video generation
│   ├── list_resources.py       # List voices & music
│   └── test_connection.py      # Validate API key
└── assets/examples/
    ├── python_client.py        # Full Python wrapper
    ├── nodejs_client.js        # Node.js implementation
    ├── curl_examples.sh        # cURL commands
    └── webhook_handler.py      # Flask webhook server
```

## API Overview

```bash
# Create video
POST /api/rest/video

# Check status
GET /api/rest/videos/{id}

# List videos
GET /api/rest/videos?limit=20&offset=0

# Translate
POST /api/rest/videos/{id}/translate?new_lang=fr

# List voices & music
GET /api/rest/voices
GET /api/rest/musics
```

## Links

- 🌐 [Fliz Website](https://fliz.ai)
- 📖 [API Documentation](https://app.fliz.ai/api-docs)
- 🔑 [Get API Key](https://app.fliz.ai/api-keys)
- 📦 [ClawdHub](https://clawdhub.com/skills/fliz-ai-video-generator)

## License

MIT — see [LICENSE.txt](LICENSE.txt)
