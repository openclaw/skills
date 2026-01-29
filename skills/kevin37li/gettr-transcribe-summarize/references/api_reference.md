# Notes / Reference

This skill assumes a simple, mostly-static GETTR post HTML page where the media URL is discoverable via `og:video*` meta tags.

## Meta tags searched
The extractor script prefers these, in order:
1. `og:video:secure_url`
2. `og:video:url`
3. `og:video`

## Output directory
`./out/gettr-transcribe-summarize/<slug>/`

The slug is the last path segment of the GETTR URL (e.g., `/post/p1abc2def` → `p1abc2def`).

## Output files
- `audio.wav` – 16kHz mono audio (optimized for Whisper)
- `audio.vtt` – timestamped transcript (VTT format)
- `summary.md` – final deliverable with bullets and optional timestamped outline

## Exit codes (extract script)
- `0`: success (video URL printed to stdout)
- `1`: no video found (post may be text/image only)
- `2`: usage error or invalid URL
- `3`: network error after retries
