---
name: ai-video-gen
description: End-to-end AI video generation - create videos from text prompts using image generation, video synthesis, voice-over, and editing. Supports OpenAI DALL-E, Replicate models, LumaAI, Runway, and FFmpeg editing.
---

# AI Video Generation Skill

Generate complete videos from text descriptions using AI.

## Capabilities

1. **Image Generation** - DALL-E 3, Stable Diffusion, Flux
2. **Video Generation** - LumaAI, Runway, Replicate models
3. **Voice-over** - OpenAI TTS, ElevenLabs
4. **Video Editing** - FFmpeg assembly, transitions, overlays

## Quick Start

```bash
# Generate a complete video
python skills/ai-video-gen/generate_video.py --prompt "A sunset over mountains" --output sunset.mp4

# Just images to video
python skills/ai-video-gen/images_to_video.py --images img1.png img2.png --output result.mp4

# Add voiceover
python skills/ai-video-gen/add_voiceover.py --video input.mp4 --text "Your narration" --output final.mp4
```

## Setup

### Required API Keys

Add to your environment or `.env` file:

```bash
# Image Generation (pick one)
OPENAI_API_KEY=sk-...              # DALL-E 3
REPLICATE_API_TOKEN=r8_...         # Stable Diffusion, Flux

# Video Generation (pick one)
LUMAAI_API_KEY=luma_...           # LumaAI Dream Machine
RUNWAY_API_KEY=...                # Runway ML
REPLICATE_API_TOKEN=r8_...        # Multiple models

# Voice (optional)
OPENAI_API_KEY=sk-...             # OpenAI TTS
ELEVENLABS_API_KEY=...            # ElevenLabs

# Or use FREE local options (no API needed)
```

### Install Dependencies

```bash
pip install openai requests pillow replicate python-dotenv
```

### FFmpeg

Already installed via winget.

## Usage Examples

### 1. Text to Video (Full Pipeline)

```bash
python skills/ai-video-gen/generate_video.py \
  --prompt "A futuristic city at night with flying cars" \
  --duration 5 \
  --voiceover "Welcome to the future" \
  --output future_city.mp4
```

### 2. Multiple Scenes

```bash
python skills/ai-video-gen/multi_scene.py \
  --scenes "Morning sunrise" "Busy city street" "Peaceful night" \
  --duration 3 \
  --output day_in_life.mp4
```

### 3. Image Sequence to Video

```bash
python skills/ai-video-gen/images_to_video.py \
  --images frame1.png frame2.png frame3.png \
  --fps 24 \
  --output animation.mp4
```

## Workflow Options

### Budget Mode (FREE)
- Image: Stable Diffusion (local or free API)
- Video: Open source models
- Voice: OpenAI TTS (cheap) or free TTS
- Edit: FFmpeg

### Quality Mode (Paid)
- Image: DALL-E 3 or Midjourney
- Video: Runway Gen-3 or LumaAI
- Voice: ElevenLabs
- Edit: FFmpeg + effects

## Scripts Reference

- `generate_video.py` - Main end-to-end generator
- `images_to_video.py` - Convert image sequence to video
- `add_voiceover.py` - Add narration to existing video
- `multi_scene.py` - Create multi-scene videos
- `edit_video.py` - Apply effects, transitions, overlays

## API Cost Estimates

- **DALL-E 3**: ~$0.04-0.08 per image
- **Replicate**: ~$0.01-0.10 per generation
- **LumaAI**: $0-0.50 per 5sec (free tier available)
- **Runway**: ~$0.05 per second
- **OpenAI TTS**: ~$0.015 per 1K characters
- **ElevenLabs**: ~$0.30 per 1K characters (better quality)

## Examples

See `examples/` folder for sample outputs and prompts.
