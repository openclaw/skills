# ComfyAI Skill for Clawdbot

## Description
Integrates with local ComfyUI instance at http://192.168.31.7:8000 to generate images from text (txt2img) and edit images using uploaded references (img2img). Uses the workflow: `~/clawd/skills/comfy-ai/image_flux2_klein_image_edit_4b_distilled.json`.

## Capabilities
- ✅ Text-to-image: Generate images from text prompts only
- ✅ Image-to-image: Edit uploaded image using a text prompt and reference image
- ✅ Returns generated image as media attachment directly to chat

## Requirements
- ComfyUI running at `http://192.168.31.7:8000`
- Workflow file located at `~/clawd/skills/comfy-ai/image_flux2_klein_image_edit_4b_distilled.json`
- `curl`, `jq`, and `python3` installed (standard on macOS)

## Usage Examples

> "Generate a cyberpunk cat wearing sunglasses"

> "Edit this image: [upload handbag_white.png] with prompt 'add neon glow and logo from reference'

## How It Works
- For **text-only**: Uses the workflow’s empty latent + positive prompt
- For **image edit**: Automatically detects uploaded image → copies it to `~/clawd/skills/comfy-ai/input/` → triggers img2img
- Generated images are saved to `~/clawd/skills/comfy-ai/output/` and returned as media attachment
- Uses Flux2-Klein-4B model with VAE and CLIP from your workflow

## Security Note
All processing happens locally. No data leaves your machine.