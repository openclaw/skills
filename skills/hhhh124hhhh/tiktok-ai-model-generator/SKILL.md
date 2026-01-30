---
name: tiktok-ai-model-generator
description: Generate AI model videos for TikTok livestreams using Pinterest, Claude, Nano Banana Pro, and Veo or Kling. Use for creating AI-generated fashion models wearing products, animating them into videos, or building automated TikTok content production workflows. This skill provides a complete 4-step workflow covering Pinterest reference selection, Claude JSON prompt generation, Nano Banana Pro image generation, and video animation. Perfect for e-commerce sellers, content creators, and TikTok marketers who need AI models to showcase products.
---

# TikTok AI Model Video Generator

Create AI-generated fashion models wearing your products and animate them into engaging TikTok livestream videos. This workflow combines multiple AI tools to produce realistic, professional product showcase content in under 5 minutes.

## Quick Start

Complete 4-step workflow to generate AI model video:

```bash
# Step 1: Select Pinterest reference
# Find a fashion pose/angle you like on Pinterest

# Step 2: Generate JSON prompt with Claude
# Ask Claude: "Give me detailed JSON prompt for this image holding [your product]"

# Step 3: Generate image with Nano Banana Pro
# Paste Claude's JSON prompt with your product image (white background)

# Step 4: Animate video with Veo or Kling
# Upload generated image to Veo/Kling and animate

# Total time: Under 5 minutes
```

## Workflow Steps

### Step 1: Pinterest Reference Selection

**Goal**: Find high-quality fashion poses that match your product's aesthetic.

**Action**: Browse Pinterest and save 2-3 reference images showing:
- Desired pose (standing, walking, sitting, etc.)
- Camera angle (full body, close-up, profile, etc.)
- Lighting style (studio, natural, dramatic)
- Background preference (clean, lifestyle, minimalist)

**Tips**:
- Search: "fashion model pose", "product photography pose", "[your product] model"
- Look for consistent brand aesthetic
- Save URLs or download images for Claude reference

---

### Step 2: Claude JSON Prompt Generation

**Goal**: Create detailed, structured prompt for Nano Banana Pro.

**Prompt Template**:

```
Give me detailed JSON prompt for this Pinterest image holding [PRODUCT DESCRIPTION]:

{
  "subject": {
    "description": "[Detailed product description]",
    "pose": "[Pose from Pinterest]",
    "angle": "[Camera angle]",
    "lighting": "[Lighting style]"
  },
  "model": {
    "appearance": "[Model physical description]",
    "outfit": "[Clothing/style details]",
    "expression": "[Facial expression]"
  },
  "environment": {
    "background": "[Background description]",
    "location": "[Setting/context]",
    "atmosphere": "[Mood/vibe]"
  },
  "technical": {
    "style": "[Photography style]",
    "camera": "[Camera settings]",
    "resolution": "[Image resolution]"
  }
}

Use the Pinterest image as visual reference for pose and composition.
```

**Claude Capabilities**:
- Analyze Pinterest image composition
- Extract pose, angle, lighting details
- Integrate product naturally into scene
- Generate JSON formatted for Nano Banana Pro

**Product Image Requirements**:
- White or neutral background
- High resolution (minimum 1024x1024)
- Clear product visibility
- Professional lighting
- No text or watermarks

---

### Step 3: Nano Banana Pro Image Generation

**Goal**: Generate photorealistic AI model wearing your product.

**Prerequisites**:
- Nano Banana Pro access (https://higgsfield.ai)
- Higgsfield account for tool access
- API key or web interface access

**Process**:
1. Open Nano Banana Pro (Higgsfield)
2. Upload your product image (white background)
3. Paste Claude's JSON prompt
4. Adjust parameters:
   - Resolution: 1024x1024 (standard)
   - Style: Photorealistic
   - Quality: High
   - Variation: Generate 2-3 options
5. Click Generate
6. Select best result

**Expected Output**:
- AI model in pose matching Pinterest reference
- Product naturally integrated into scene
- Photorealistic quality (professional photography)
- Consistent lighting and shadows
- White/neutral background (easier for video editing)

**Troubleshooting**:
- **Product not visible**: Check JSON prompt includes product description clearly
- **Pose mismatch**: Add more specific pose instructions to JSON
- **Unrealistic**: Lower "style strength" or adjust "model appearance" details
- **Lighting issues**: Specify "studio lighting" in environment section

---

### Step 4: Veo/Kling Video Animation

**Goal**: Animate generated image into engaging TikTok video.

**Tool Options**:

#### Veo (Google's AI Video Generator)
- Access: Via Higgsfield platform
- Input: Generated image from Nano Banana Pro
- Output: Animated video (3-10 seconds)
- Features:
  - Natural movement
  - Product-focused animation
  - High quality (1080p+)

**Animation Prompts**:
```
Prompt ideas for Veo:
- "Subtle body sway, arms gently moving, natural breathing motion"
- "Model turning slightly to show product from different angles"
- "Small hand gestures highlighting product features"
- "Natural head movement, facial expression changes"
- "Walking slowly, product clearly visible"
```

#### Kling AI Video Generator
- Alternative to Veo
- Similar workflow
- May offer different animation styles
- Check which produces better results for your use case

**Process**:
1. Upload Nano Banana Pro generated image
2. Choose animation style (subtle, dynamic, product-focused)
3. Enter animation prompt (see above)
4. Generate 3-5 second video
5. Review and refine if needed
6. Export for TikTok upload

**Video Settings**:
- Duration: 3-5 seconds (optimal for TikTok)
- Resolution: 1080x1920 (9:16 vertical)
- Frame rate: 24-30 fps
- Format: MP4 (TikTok compatible)

---

## Use Cases

### E-commerce Product Showcase
- **Perfect for**: Fashion, jewelry, accessories, cosmetics
- **Workflow**: Generate AI models in multiple poses
- **Output**: Product-focused videos showcasing features
- **Time**: 5 minutes per video (vs. hours of traditional shoots)

### TikTok Livestream Content
- **Use case**: 24/7 AI model livestreams (as mentioned by @barkmeta)
- **Workflow**: Generate variations, animate, loop
- **Advantage**: Scalable, no human models needed
- **Platforms**: TikTok, Instagram, YouTube Shorts

### Social Media Marketing
- **Platforms**: TikTok, Instagram Reels, YouTube Shorts
- **Content types**:
  - Product launches
  - Feature highlights
  - Seasonal collections
  - A/B testing different styles

---

## Optimization Tips

### Better Results

1. **Pinterest Reference Quality**:
   - Choose high-resolution images
   - Match your brand aesthetic
   - Consider lighting conditions

2. **Prompt Specificity**:
   - Be detailed in JSON structure
   - Include lighting, camera, and style
   - Reference Pinterest image explicitly

3. **Product Preparation**:
   - Clean, white background essential
   - Professional photography quality
   - Multiple angles available

4. **Animation Subtlety**:
   - Natural movements (no jerky motions)
   - Focus on product visibility
   - Keep videos short (3-5 seconds)

### Time Optimization

**Batch Workflow**:
1. Generate 10-20 images at once (Nano Banana Pro batch)
2. Animate top 3-5 selections
3. Create content calendar (week/month)
4. Schedule TikTok posts

**Tools Access**:
- Save Claude JSON prompts as templates
- Reuse successful prompts for similar products
- Build prompt library for faster iteration

---

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|--------|----------|
| Product not visible | JSON prompt unclear | Add explicit "product in foreground" instructions |
| AI model looks fake | Low quality generation | Increase resolution, adjust "model appearance" details |
| Animation unnatural | Incorrect prompt | Use subtle motion keywords (gentle, natural, breathing) |
| Video format wrong | Resolution mismatch | Export 1080x1920 vertical format for TikTok |
| Lighting inconsistent | Different tools used | Match lighting settings across all steps |

---

## Advanced Techniques

### Multi-Pose Product Showcase
1. Generate 3 different poses (front, side, detail)
2. Animate each individually
3. Combine into longer TikTok video
4. Add transitions between poses

### A/B Testing
1. Create 2-3 variations of same product
2. Test different poses/backgrounds
3. Compare engagement metrics
4. Optimize for best performing style

### Seasonal Collections
1. Update JSON prompts for seasonal context
2. Change lighting (warm for summer, cool for winter)
3. Adjust background themes
4. Generate themed video sets

---

## Required Tools

All tools accessible via [Higgsfield](https://higgsfield.ai):

1. **Claude AI** - JSON prompt generation
2. **Nano Banana Pro** - Photorealistic image generation
3. **Veo 3.1** - Video animation
4. **Kling AI** - Alternative video generator

**Alternative Workflows**:
- Replace Claude with GPT-4 (if available)
- Replace Nano Banana with Midjourney/DALL-E
- Replace Veo with Runway ML/Pika Labs

---

## Cost & Time Estimate

**Per Video**:
- Time: 3-5 minutes
- Tools: Free tier available (check limits)
- Commercial use: Verify tool licensing terms

**Batch Production**:
- 10 videos: ~30-60 minutes
- 50 videos: ~2.5-4 hours
- Scale: Unlimited (with tool API access)

**Comparison**:
- Traditional photoshoot: $500-$2,000+ per day
- AI workflow: Free to $50/month (subscription)
- Time savings: 95%+ reduction

---

## Troubleshooting

### Tool Access Issues
- **Higgsfield account**: Create free account at https://higgsfield.ai
- **API rate limits**: Check free tier limits, consider upgrade
- **Login problems**: Clear browser cache, try different browser

### Quality Issues
- **Low resolution**: Increase image resolution to 2048x2048
- **Artifacts**: Regenerate with different random seed
- **Inconsistent style**: Use same JSON prompt template for batch

### Animation Problems
- **Jerky motion**: Simplify animation prompt, use "subtle" keywords
- **Product out of frame**: Add "keep product in frame" to prompt
- **Too fast**: Reduce movement in prompt, extend duration

---

## Examples

### Jewelry Product
```
Pinterest: Minimalist gold necklace, model looking down
Product: Gold chain necklace on white background
Claude Prompt: "Generate JSON for pendant necklace, model looking down, studio lighting"
Nano Banana: Photorealistic close-up
Veo Animation: "Gentle sway, necklace catching light"
```

### Fashion Item
```
Pinterest: Full body fashion pose, walking stance
Product: White t-shirt, lifestyle setting
Claude Prompt: "Generate JSON for casual wear, walking motion, outdoor lighting"
Nano Banana: Full body photorealistic
Veo Animation: "Natural walking motion, arms gently swinging"
```

### Accessory
```
Pinterest: Hand holding phone case, focus on product
Product: Designer phone case
Claude Prompt: "Generate JSON for phone case in hand, close-up, clean background"
Nano Banana: High detail macro shot
Veo Animation: "Subtle hand movement, showing product angles"
```

---

## File Structure

```
tiktok-ai-model-generator/
├── SKILL.md (this file)
├── scripts/
│   └── generate_workflow.py (optional automation script)
└── references/
    ├── pinterest_tips.md (Pinterest selection guide)
    └── prompt_templates.md (Reusable JSON templates)
```

See bundled scripts and references for automation tools and detailed templates.
