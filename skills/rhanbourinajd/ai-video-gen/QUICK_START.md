# Quick Start - Get Your First Video in 5 Minutes

## Step 1: Get OpenAI API Key (Required)

1. Go to https://platform.openai.com/api-keys
2. Sign up / Log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

**Cost:** You'll need ~$5 credit. First video costs ~$0.10

## Step 2: Get LumaAI Key (Optional but Recommended)

1. Go to https://lumalabs.ai
2. Sign up (has free tier!)
3. Get API key from dashboard

**Cost:** FREE for first 30 videos/month

## Step 3: Configure

Create `.env` file:

```bash
cd skills/ai-video-gen
copy .env.example .env
```

Edit `.env` and add:
```
OPENAI_API_KEY=sk-your-actual-key-here
LUMAAI_API_KEY=luma_your-actual-key-here
```

## Step 4: Generate Video!

```bash
python generate_video.py --prompt "A peaceful forest with sunlight filtering through trees" --output forest.mp4
```

With narration:
```bash
python generate_video.py \
  --prompt "A robot walking through a futuristic city" \
  --voiceover "In the year 2050, robots walk among us" \
  --output robot.mp4
```

## What Happens

1. 🎨 Generates image from your prompt (DALL-E 3)
2. 🎬 Converts image to 5-second video (LumaAI)
3. 🎤 Creates voiceover if requested (OpenAI TTS)
4. ✅ Combines everything into final MP4

**Time:** 30-60 seconds per video
**Cost:** $0.05-0.15 per video

## Without LumaAI Key

If you don't have LumaAI yet, you can still:

**Create image + audio:**
```bash
python generate_video.py --prompt "sunset" --output sunset.mp4
# (Will fail at video step, but you'll have the image!)
```

**Convert images to video:**
```bash
python images_to_video.py --images img1.png img2.png img3.png --output result.mp4
```

## Next Steps

- Try different prompts
- Experiment with voices (alloy, echo, fable, onyx, nova, shimmer)
- Create longer videos by chaining scenes
- Add music and effects

Need help? Check `README.md` for full docs!
