---
name: gettr-transcribe-summarize
description: Download audio from a GETTR post (via HTML og:video), transcribe it locally with MLX Whisper on Apple Silicon (with timestamps via VTT), and summarize the transcript into bullet points and/or a timestamped outline. Use when given a GETTR post URL and asked to produce a transcript or summary.
homepage: https://gettr.com
metadata: {"clawdbot":{"emoji":"📺","requires":{"bins":["mlx_whisper","ffmpeg"]},"install":[{"id":"mlx-whisper","kind":"pip","package":"mlx-whisper","bins":["mlx_whisper"],"label":"Install mlx-whisper (pip)"},{"id":"ffmpeg","kind":"brew","formula":"ffmpeg","bins":["ffmpeg"],"label":"Install ffmpeg (brew)"}]}}
---

# Gettr Transcribe + Summarize (MLX Whisper)

## Quick start

```bash
# 1. Parse the slug from the URL (just read it — no script needed)
#    https://gettr.com/post/p1abc2def  → slug = p1abc2def
#    https://gettr.com/streaming/p3xyz → slug = p3xyz

# 2. Get the video URL
#    For /post/ URLs: use the extraction script
python3 scripts/extract_gettr_og_video.py "<GETTR_POST_URL>"

#    For /streaming/ URLs: use browser automation directly (extraction script is unreliable)
#    See Step 1 below for browser automation instructions

# 3. Run download + transcription pipeline
bash scripts/run_pipeline.sh "<VIDEO_URL>" "<SLUG>"
```

To explicitly set the transcription language (recommended for non-English content):
```bash
bash scripts/run_pipeline.sh --language zh "<VIDEO_URL>" "<SLUG>"
```

Common language codes: `zh` (Chinese), `en` (English), `ja` (Japanese), `ko` (Korean), `es` (Spanish), `fr` (French), `de` (German), `ru` (Russian).

This outputs:
- `./out/gettr-transcribe-summarize/<slug>/audio.wav`
- `./out/gettr-transcribe-summarize/<slug>/audio.vtt`

Then proceed to Step 3 (Summarize) to generate the final deliverable.

---

## Workflow (GETTR URL → transcript → summary)

### Inputs to confirm
Ask for:
- GETTR post URL
- Output format: **bullets only** or **bullets + timestamped outline**
- Summary size: **short**, **medium** (default), or **detailed**
- Language (optional): if the video is non-English and auto-detection fails, ask for the language code (e.g., `zh` for Chinese)

Notes:
- This skill does **not** handle authentication-gated GETTR posts.
- This skill does **not** translate; outputs stay in the video's original language.
- If transcription quality is poor or mixed with English, re-run with explicit `--language` flag.

### Prereqs (local)
- `mlx_whisper` installed and on PATH
- `ffmpeg` installed (recommended: `brew install ffmpeg`)

### Step 0 — Parse the slug and pick an output directory

Parse the slug directly from the GETTR URL — just read the last path segment, no script needed:
- `https://gettr.com/post/p1abc2def` → slug = `p1abc2def`
- `https://gettr.com/streaming/p3xyz789` → slug = `p3xyz789`

Output directory: `./out/gettr-transcribe-summarize/<slug>/`

Directory structure:
- `./out/gettr-transcribe-summarize/<slug>/audio.wav`
- `./out/gettr-transcribe-summarize/<slug>/audio.vtt`
- `./out/gettr-transcribe-summarize/<slug>/summary.md`

### Step 1 — Get the video URL

The approach depends on the URL type:

#### For `/post/` URLs — Use the extraction script

Run the extraction script to get the video URL from the post HTML:

```bash
python3 scripts/extract_gettr_og_video.py "<GETTR_POST_URL>"
```

This prints the best candidate video URL (often an HLS `.m3u8`) to stdout.

If extraction fails, ask the user to provide the `.m3u8`/MP4 URL directly (common if the post is private/gated or the HTML is dynamic).

#### For `/streaming/` URLs — Use browser automation directly

**Do not use the extraction script for streaming URLs.** The `og:video` URL from static HTML extraction is unreliable for streaming content — it either fails outright or the download stalls and fails near the end.

Instead, use browser automation to get a fresh, dynamically-signed URL:
1. Open the GETTR streaming URL and wait for the page to fully load (JavaScript must execute)
2. Extract the `og:video` meta tag content from the rendered DOM:
   ```javascript
   document.querySelector('meta[property="og:video"]').getAttribute('content')
   ```
3. Use that fresh URL for the pipeline in Step 2

If browser automation is not available or fails, see `references/troubleshooting.md` for how to guide the user to manually extract the fresh URL from their browser.

### Step 2 — Run the pipeline (download + transcribe)

Feed the extracted video URL and slug into the pipeline:

```bash
bash scripts/run_pipeline.sh "<VIDEO_URL>" "<SLUG>"
```

To explicitly set the language (recommended when auto-detection fails):
```bash
bash scripts/run_pipeline.sh --language zh "<VIDEO_URL>" "<SLUG>"
```

The pipeline does two things:
1. Downloads audio as 16kHz mono WAV via ffmpeg
2. Transcribes with MLX Whisper, outputting VTT with timestamps

#### If the pipeline fails with HTTP 412 (stale signed URL)

This error occurs with `/streaming/` URLs when the signed URL has expired. If browser automation returned a stale URL, retry by re-running browser automation to get a fresh URL, then retry the pipeline.

If browser automation is not available or fails, see `references/troubleshooting.md` for how to guide the user to manually extract the fresh URL from their browser.

Notes:
- By default, language is auto-detected. For non-English content where detection fails, use `--language`.
- If too slow or memory-heavy, try smaller models: `mlx-community/whisper-medium` or `mlx-community/whisper-small`.
- If quality is poor, try the full model: `mlx-community/whisper-large-v3` (slower but more accurate).
- If `--word-timestamps` causes issues, the pipeline retries automatically without it.

### Step 3 — Summarize
Write the final deliverable to `./out/gettr-transcribe-summarize/<slug>/summary.md`.

Pick a **summary size** (user-selectable):
- **Short:** 5–8 bullets; (if outline) 4–6 sections
- **Medium (default):** 8–20 bullets; (if outline) 6–15 sections
- **Detailed:** 20–40 bullets; (if outline) 15–30 sections

Include:
- **Bullets** (per size above)
- Optional **timestamped outline** (per size above)

Timestamped outline format (default heading style):
```
[00:00 - 02:15] Section heading
- 1–3 sub-bullets
```

When building the outline from VTT cues:
- Group adjacent cues into coherent sections.
- Use the start time of the first cue and end time of the last cue in the section.

## Bundled scripts
- `scripts/run_pipeline.sh`: download + transcription pipeline (takes a video URL and slug)
- `scripts/extract_gettr_og_video.py`: fetch GETTR HTML and extract the `og:video` URL (with retry/backoff)
- `scripts/download_audio.sh`: download/extract audio from HLS or MP4 URL to 16kHz mono WAV

### Error handling
- **Non-video posts**: The extraction script detects image/text posts and provides a helpful error message.
- **Network errors**: Automatic retry with exponential backoff (up to 3 attempts).
- **No audio track**: The download script validates output and reports if the source has no audio.
- **HTTP 412 errors**: Occurs with `/streaming/` URLs when the signed URL has expired. Re-run browser automation to get a fresh URL (see Step 1); if that fails, see `references/troubleshooting.md`.

## Troubleshooting
See `references/troubleshooting.md` for detailed solutions to common issues including:
- HTTP 412 errors (stale signed URLs)
- Extraction failures
- Download errors
- Transcription quality issues
