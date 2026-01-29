# Gettr Transcript & Summary

Download audio from a GETTR post, transcribe it locally with MLX Whisper on Apple Silicon, and produce a clean summary or timestamped outline.

## What it does
- Extracts audio from a GETTR post (via og:video → 16kHz mono WAV)
- Transcribes locally with MLX Whisper (no API keys required)
- Outputs VTT with timestamps for precise outline generation
- Summarizes into bullets or a timestamped outline

## Quick start
```bash
# For /post/ URLs: extract the og:video URL via script
python3 scripts/extract_gettr_og_video.py "<GETTR_POST_URL>"

# For /streaming/ URLs: use browser automation directly (see SKILL.md Step 1)
# The extraction script is unreliable for streaming URLs

# Run download + transcription (slug is the last path segment of the URL)
bash scripts/run_pipeline.sh "<VIDEO_URL>" "<SLUG>"
```

Outputs to `./out/gettr-transcribe-summarize/<slug>/`:
- `audio.wav` – extracted audio
- `audio.vtt` – timestamped transcript

## Prerequisites
- `mlx_whisper` (`pip install mlx-whisper`)
- `ffmpeg` (`brew install ffmpeg`)

## Features
- Auto-detects non-video posts (image/text) with helpful error messages
- Retries network requests with exponential backoff
- Transcribes in original language (auto-detected)
- Prevents hallucination propagation with `--condition_on_previous_text False`
