---
name: parakeet-mlx
description: Local speech-to-text with Parakeet MLX (ASR) for Apple Silicon (no API key).
homepage: https://github.com/senstella/parakeet-mlx
metadata: {"clawdbot":{"emoji":"🦜","requires":{"bins":["parakeet-mlx"]},"install":[{"id":"uv-tool","kind":"uv","formula":"parakeet-mlx","bins":["parakeet-mlx"],"label":"Install Parakeet MLX CLI (uv tool install)"}]}}
---

# Parakeet MLX (CLI)

Use `parakeet-mlx` to transcribe audio locally on Apple Silicon.

Quick start
- `parakeet-mlx /path/audio.mp3 --output-format txt`
- `parakeet-mlx /path/audio.m4a --output-format vtt --highlight-words`
- `parakeet-mlx *.mp3 --output-format all`

Notes
- Install CLI with: `uv tool install parakeet-mlx -U` (not `uv add` or `pip install`)
- Use `parakeet-mlx --help` to see all options (`--help`, not `-h`).
- Models download from Hugging Face to `~/.cache/huggingface` on first run.
- Default model: `mlx-community/parakeet-tdt-0.6b-v3` (optimized for Apple Silicon).
- Requires `ffmpeg` installed for audio processing.
- Output formats: txt, srt, vtt, json, or all.
- Use `--verbose` for detailed progress and confidence scores.
- Accepts multiple files (shell wildcards like `*.mp3` work).
