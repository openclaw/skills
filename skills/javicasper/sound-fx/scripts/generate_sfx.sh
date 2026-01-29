#!/usr/bin/env bash
set -euo pipefail

TEXT=""
OUT=""
DURATION=""
MODEL="eleven_text_to_sound_v2"
FORMAT="mp3_44100_128"
PROMPT_INFLUENCE="0.3"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --text)
      TEXT="$2"; shift 2;;
    --out)
      OUT="$2"; shift 2;;
    --duration)
      DURATION="$2"; shift 2;;
    --model)
      MODEL="$2"; shift 2;;
    --format)
      FORMAT="$2"; shift 2;;
    --prompt-influence)
      PROMPT_INFLUENCE="$2"; shift 2;;
    -h|--help)
      echo "Usage: $0 --text \"prompt\" --out /path/out.mp3 [--duration 1.5] [--model eleven_text_to_sound_v2] [--format mp3_44100_128] [--prompt-influence 0.3]"
      exit 0;;
    *)
      echo "Unknown arg: $1"; exit 1;;
  esac
 done

if [[ -z "$TEXT" || -z "$OUT" ]]; then
  echo "--text and --out are required" >&2
  exit 1
fi

API_KEY="${ELEVENLABS_API_KEY:-${XI_API_KEY:-}}"
if [[ -z "$API_KEY" ]]; then
  echo "Missing ELEVENLABS_API_KEY (or XI_API_KEY)" >&2
  exit 1
fi

export SFX_TEXT="$TEXT"
export SFX_MODEL="$MODEL"
export SFX_PROMPT_INFLUENCE="$PROMPT_INFLUENCE"
export SFX_DURATION="$DURATION"
PAYLOAD=$(python3 - <<'PY'
import json, os
text = os.environ.get("SFX_TEXT")
model = os.environ.get("SFX_MODEL")
prompt_influence = float(os.environ.get("SFX_PROMPT_INFLUENCE", "0.3"))
duration = os.environ.get("SFX_DURATION")
body = {
  "text": text,
  "model_id": model,
  "prompt_influence": prompt_influence,
}
if duration:
  body["duration_seconds"] = float(duration)
print(json.dumps(body))
PY
)

HTTP_CODE=$(curl -sS -o "$OUT" -w "%{http_code}" \
  -X POST "https://api.elevenlabs.io/v1/sound-generation?output_format=${FORMAT}" \
  -H "xi-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "SFX request failed (HTTP $HTTP_CODE)" >&2
  echo "Response:" >&2
  cat "$OUT" >&2
  exit 1
fi

echo "Saved: $OUT"
echo "MEDIA: $OUT"
