---
name: infographic-weather
description: Generate a TV-style weather infographic with a location-specific seasonal background. Use when the user asks for a visual weather forecast or a weather infographic for a specific address.
metadata: {"clawdbot":{"emoji":"📺","requires":{"env":["GEMINI_API_KEY"]},"install":[{"id":"pip-google-ai","kind":"exec","command":"pip install -U google-generativeai requests --break-system-packages","label":"Install dependencies"}]}}
---

# Infographic Weather

Generate a professional TV-style weather broadcast frame using Gemini 3 Pro Image (Nano Banana).

## Features
- **Seasonal Backgrounds**: Generates a photorealistic backdrop based on the address and current New Zealand season.
- **Real-time Data**: Pulls live weather and 7-day forecast from Open-Meteo.
- **Broadcast UI**: Stitches data and background into a professional TV broadcast layout.

## Usage

```bash
python3 {baseDir}/scripts/generate_infographic.py --address "488 Riddell Road, Saint Heliers, Auckland" --lat -36.8501 --lon 174.8699 --output "out/weather-$(date +%F).png"
```

## Environment
- `GEMINI_API_KEY`: Required for image generation.
