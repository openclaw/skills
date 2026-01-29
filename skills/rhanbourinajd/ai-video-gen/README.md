# AI Video Generator

Complete end-to-end AI video creation system.

## ✅ Installation Status

- [x] FFmpeg installed
- [x] Python 3.11.9 available
- [ ] Python dependencies (run `setup.bat`)
- [ ] API keys configured

## Quick Start

### 1. Install Dependencies

```bash
cd skills/ai-video-gen
pip install -r requirements.txt
```

Or run `setup.bat`

### 2. Configure API Keys

Copy `.env.example` to `.env` and add your keys:

```bash
copy .env.example .env
notepad .env
```

**Minimum required:**
- `OPENAI_API_KEY` - For both image (DALL-E) and voice (TTS)

**Optional but recommended:**
- `LUMAAI_API_KEY` - For video generation (has free tier!)
- `REPLICATE_API_TOKEN` - Alternative for images/video

### 3. Generate Your First Video

```bash
python generate_video.py --prompt "A serene mountain landscape at sunset" --output test.mp4
```

With voiceover:

```bash
python generate_video.py \
  --prompt "A futuristic city with flying cars" \
  --voiceover "Welcome to the future" \
  --output future.mp4
```

## What You Need to Sign Up For

### Free/Cheap Options (Start Here)

1. **OpenAI** - https://platform.openai.com
   - Get API key for DALL-E + TTS
   - Cost: ~$0.05-0.10 per video (image + voice)
   
2. **LumaAI** - https://lumalabs.ai
   - Free tier: 30 generations/month
   - Then $1-2 per video

**Total cost to start: $0-0.15 per video**

### Premium Options (Better Quality)

3. **Runway** - https://runwayml.com
   - Higher quality video generation
   - ~$0.50-1.00 per 5-second video

4. **ElevenLabs** - https://elevenlabs.io
   - Best voice quality
   - ~$0.30 per 1K characters

5. **Replicate** - https://replicate.com
   - Multiple AI models
   - Pay-per-use, very cheap

## Examples

### Simple Video
```bash
python generate_video.py --prompt "Ocean waves crashing" --output waves.mp4
```

### Multi-Image to Video
```bash
python images_to_video.py --images img1.png img2.png img3.png --output slideshow.mp4
```

### Add Narration to Existing Video
```bash
python add_voiceover.py --video input.mp4 --text "Your narration here" --output final.mp4
```

## Workflow

```
Text Prompt → DALL-E Image → LumaAI Video → + Voiceover → Final MP4
```

All automated in one command!

## Cost Calculator

**Budget Video (5 seconds):**
- Image (DALL-E): $0.04
- Video (LumaAI free): $0
- Voice (OpenAI TTS): $0.01
- **Total: $0.05**

**Quality Video (5 seconds):**
- Image (DALL-E): $0.08
- Video (Runway): $0.50
- Voice (ElevenLabs): $0.30
- **Total: $0.88**

## Troubleshooting

### FFmpeg not found
Restart your terminal after installation, or add to PATH manually.

### API Key errors
Make sure `.env` file exists and has valid keys (no quotes needed).

### Python module errors
Run `pip install -r requirements.txt`

## What's Next

The scripts are modular - you can:
- Use just image generation
- Use just video assembly from images
- Add effects and transitions
- Batch process multiple videos
- Create longer videos with scene transitions

Need help? Check the examples or ask!
