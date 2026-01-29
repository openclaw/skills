#!/usr/bin/env bash
set -euo pipefail

# GETTR Transcribe Pipeline
# Usage: run_pipeline.sh [--language <code>] <video_url> <slug> [output_base_dir]
#
# Runs download + transcription for a GETTR video:
#   1. Download audio (16kHz mono WAV)
#   2. Transcribe with MLX Whisper (VTT output)
#
# The og:video extraction should be done BEFORE calling this script
# (see extract_gettr_og_video.py or browser extraction for streaming URLs).
#
# Output: <output_base_dir>/gettr-transcribe-summarize/<slug>/
#   - audio.wav
#   - audio.vtt
#
# The summary step is left to the LLM.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Parse optional --language flag
LANGUAGE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --language|-l)
      if [[ -n "${2:-}" ]]; then
        LANGUAGE="$2"
        shift 2
      else
        echo "[error] --language requires a language code (e.g., zh, en, ja)" >&2
        exit 2
      fi
      ;;
    -*)
      echo "[error] Unknown option: $1" >&2
      exit 2
      ;;
    *)
      break
      ;;
  esac
done

if [[ $# -lt 2 ]]; then
  echo "Usage: run_pipeline.sh [--language <code>] <video_url> <slug> [output_base_dir]" >&2
  echo "" >&2
  echo "Arguments:" >&2
  echo "  video_url        The video/HLS URL (from og:video extraction or browser)" >&2
  echo "  slug             The post slug (e.g., p1abc2def)" >&2
  echo "" >&2
  echo "Options:" >&2
  echo "  --language, -l   Language code for transcription (e.g., zh, en, ja, ko)" >&2
  echo "                   If not specified, language is auto-detected." >&2
  echo "  output_base_dir  Base directory for output (default: ./out)" >&2
  echo "" >&2
  echo "Common language codes:" >&2
  echo "  zh = Chinese, en = English, ja = Japanese, ko = Korean" >&2
  echo "  es = Spanish, fr = French, de = German, ru = Russian" >&2
  exit 2
fi

VIDEO_URL="$1"
SLUG="$2"
OUTPUT_BASE="${3:-./out}"

# Check prerequisites
for cmd in ffmpeg mlx_whisper; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "[error] Required command not found: $cmd" >&2
    if [[ "$cmd" == "ffmpeg" ]]; then
      echo "[hint] Install with: brew install ffmpeg" >&2
    elif [[ "$cmd" == "mlx_whisper" ]]; then
      echo "[hint] Install with: pip install mlx-whisper" >&2
    fi
    exit 127
  fi
done

echo "[info] Video URL: $VIDEO_URL" >&2
echo "[info] Slug: $SLUG" >&2

# Set up output directory
OUT_DIR="$OUTPUT_BASE/gettr-transcribe-summarize/$SLUG"
mkdir -p "$OUT_DIR"

AUDIO_FILE="$OUT_DIR/audio.wav"
VTT_FILE="$OUT_DIR/audio.vtt"

echo "" >&2
echo "=== Step 1: Downloading audio ===" >&2

"$SCRIPT_DIR/download_audio.sh" "$VIDEO_URL" "$AUDIO_FILE" >&2 || {
  echo "[error] Failed to download audio" >&2
  exit 1
}

echo "[info] Audio saved: $AUDIO_FILE" >&2

echo "" >&2
echo "=== Step 2: Transcribing with MLX Whisper ===" >&2

# MLX Whisper transcription with optimized flags:
# -f vtt: VTT format for timestamps
# --condition-on-previous-text False: prevents hallucination propagation
# --word-timestamps True: more precise timing (if supported)
# --language: explicit language if provided (otherwise auto-detected)

# Build language flag if specified
LANG_FLAG=""
if [[ -n "$LANGUAGE" ]]; then
  LANG_FLAG="--language $LANGUAGE"
  echo "[info] Using explicit language: $LANGUAGE" >&2
else
  echo "[info] Language will be auto-detected" >&2
fi

mlx_whisper "$AUDIO_FILE" \
  -f vtt \
  -o "$OUT_DIR" \
  --model mlx-community/whisper-large-v3-turbo \
  --condition-on-previous-text False \
  --word-timestamps True \
  $LANG_FLAG \
  2>&1 || {
    echo "[warn] Retrying without extra flags..." >&2
    mlx_whisper "$AUDIO_FILE" \
      -f vtt \
      -o "$OUT_DIR" \
      --model mlx-community/whisper-large-v3-turbo \
      $LANG_FLAG
  }

echo "[info] Transcript saved: $VTT_FILE" >&2

echo "" >&2
echo "=== Pipeline complete ===" >&2
echo "[info] Output directory: $OUT_DIR" >&2
echo "" >&2

# Output the paths for programmatic use (stdout)
echo "$OUT_DIR"
echo "$AUDIO_FILE"
echo "$VTT_FILE"
