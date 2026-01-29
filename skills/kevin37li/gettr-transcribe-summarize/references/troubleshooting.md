# Troubleshooting (GETTR → ffmpeg → MLX Whisper)

## Prerequisites not found

### ffmpeg not found
Install on macOS:
```bash
brew install ffmpeg
```

### mlx_whisper not found
Install with pip:
```bash
pip install mlx-whisper
```

## Extraction errors

### "This appears to be an image post, not a video"
The extraction script detected that the GETTR post contains an image, not a video. This skill only works with video posts.

### "This appears to be a text/article post, not a video"
The GETTR post is text-only and has no media to transcribe.

### "No og:video meta tag found"
Possible causes:
- GETTR may be serving different HTML to different user agents, or the content is loaded dynamically.
- Try opening the post in a browser and **View Source**; confirm an `og:video` meta tag exists.
- If the page requires auth/JS rendering, you may need a different fetch method (e.g., browser automation) instead of a plain HTTP fetch.

### Network errors / retries exhausted
The extraction script retries up to 3 times with exponential backoff. If it still fails:
- Check your internet connection.
- The GETTR server may be temporarily unavailable; try again later.
- Try fetching the URL manually in a browser to confirm it's accessible.

## Download errors

### "Failed to extract audio" / "Output file is empty"
The source URL may not contain an audio track, or the stream format is unsupported. Try:
- Verifying the URL plays in a browser or VLC.
- If it's an HLS stream, ensure ffmpeg was built with HLS support.

### ffmpeg download fails on HLS (.m3u8)
If the playlist uses redirects, test manually:
```bash
ffmpeg -hide_banner -loglevel warning -i "<m3u8>" -t 00:00:30 -vn -ac 1 -ar 16000 /tmp/test.wav
```

### HTTP 412 Precondition Failed
This error occurs with `/streaming/` URLs when the signed URL has expired. For streaming URLs, you should already be using browser automation to get the video URL (see SKILL.md Step 1). If the URL still expired, re-run browser automation to get a fresh one.

If browser automation is not available, guide the user to manually extract the fresh URL:
1. Open the GETTR page in their browser and wait for it to fully load
2. Open DevTools (F12) → Elements tab → search for `og:video`
3. Copy the `content` attribute value from the `og:video` meta tag
4. Provide that URL to retry the pipeline

## Private/gated GETTR posts (auth)
This skill does **not** handle GETTR authentication.

If extraction fails because the post is private/gated or requires JS:
- Ask the user for a direct `.m3u8` or MP4 URL, or
- Use a browser/manual approach to retrieve the media URL.

## Transcription issues

### Hallucinations / repeated phrases
Use `--condition_on_previous_text False` (included in the pipeline by default) to prevent errors from propagating.

### Poor transcription quality
- Try a larger model: `mlx-community/whisper-large-v3`
- Check audio clarity (background noise, multiple speakers)
- Ensure the audio is in a supported language

### word-timestamps not supported
Some MLX Whisper versions may not support `--word-timestamps`. The pipeline script automatically falls back if this flag fails.

### HuggingFace 401 / Repository Not Found
If you see `401 Client Error` or `Repository Not Found`:
- The model may require HuggingFace authentication: `huggingface-cli login`
- Check the model name is correct (e.g., `mlx-community/whisper-large-v3-turbo`)
- Some models may have been renamed or removed

