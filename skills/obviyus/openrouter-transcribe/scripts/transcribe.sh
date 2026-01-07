#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  transcribe.sh <audio-file> [options]

Options:
  --model <model>    OpenRouter model (default: google/gemini-2.5-flash)
  --prompt <text>    Custom transcription instructions
  --out <file>       Output file (default: stdout)
  --title <name>     Caller identifier for OpenRouter (default: Clawdbot)
  --referer <url>    HTTP-Referer header (default: https://clawdbot.com)

Example:
  transcribe.sh audio.m4a --prompt "Include timestamps"
EOF
  exit 2
}

if [[ "${1:-}" == "" || "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
fi

in="${1:-}"
shift || true

model="google/gemini-2.5-flash"
prompt="Please transcribe this audio file. Keep it readable, suitable for messaging. Begin transcript immediately without any commentary."
out=""
title="Clawdbot"
referer="https://clawdbot.com"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      model="${2:-}"
      shift 2
      ;;
    --prompt)
      prompt="${2:-}"
      shift 2
      ;;
    --out)
      out="${2:-}"
      shift 2
      ;;
    --title)
      title="${2:-}"
      shift 2
      ;;
    --referer)
      referer="${2:-}"
      shift 2
      ;;
    *)
      echo "Unknown arg: $1" >&2
      usage
      ;;
  esac
done

if [[ ! -f "$in" ]]; then
  echo "File not found: $in" >&2
  exit 1
fi

if [[ "${OPENROUTER_API_KEY:-}" == "" ]]; then
  echo "Missing OPENROUTER_API_KEY" >&2
  exit 1
fi

# Create temp files for conversion
tmp_dir=$(mktemp -d)
tmp_wav="$tmp_dir/audio.wav"
trap 'rm -rf "$tmp_dir"' EXIT

# Convert audio to WAV (mono, 16kHz) using ffmpeg
if ! ffmpeg -y -i "$in" -ac 1 -ar 16000 "$tmp_wav" 2>/dev/null; then
  echo "ffmpeg failed to convert audio" >&2
  exit 1
fi

# Base64 encode the WAV file
audio_base64=$(base64 < "$tmp_wav" | tr -d '\n')

# Build JSON payload using jq for proper escaping
# Write base64 to file first to avoid "argument list too long" errors
echo "$audio_base64" > "$tmp_dir/audio.b64"
payload_file="$tmp_dir/payload.json"
jq -n \
  --arg model "$model" \
  --arg prompt "$prompt" \
  --rawfile audio "$tmp_dir/audio.b64" \
  '{
    model: $model,
    messages: [{
      role: "user",
      content: [
        { type: "text", text: $prompt },
        { type: "input_audio", input_audio: { data: ($audio | rtrimstr("\n")), format: "wav" } }
      ]
    }]
  }' > "$payload_file"

# Make API request
response=$(curl -sS "https://openrouter.ai/api/v1/chat/completions" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Title: $title" \
  -H "HTTP-Referer: $referer" \
  -d "@$payload_file")

# Check for API errors first
if echo "$response" | jq -e '.error' >/dev/null 2>&1; then
  error_msg=$(echo "$response" | jq -r '.error.message // .error // "Unknown API error"')
  echo "API error: $error_msg" >&2
  exit 1
fi

# Extract transcript
transcript=$(echo "$response" | jq -r '.choices[0].message.content // empty')

if [[ -z "$transcript" ]]; then
  echo "Empty response from API. Raw response:" >&2
  echo "$response" | head -c 500 >&2
  exit 1
fi

if [[ "$out" != "" ]]; then
  mkdir -p "$(dirname "$out")"
  echo "$transcript" > "$out"
  echo "$out"
else
  echo "$transcript"
fi
