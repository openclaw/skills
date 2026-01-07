#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CREDS_DIR="${CLAWDBOT_CREDENTIALS:-$HOME/.clawdbot/credentials}/pocket-casts"
CONFIG_FILE="$CREDS_DIR/config.json"
COOKIES_FILE="$CREDS_DIR/cookies.txt"
TEMP_DIR="/tmp/pocket-casts-upload"

# Add deno to PATH if installed
export PATH="$HOME/.deno/bin:$PATH"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[pocket-casts]${NC} $1"; }
warn() { echo -e "${YELLOW}[pocket-casts]${NC} $1"; }
err() { echo -e "${RED}[pocket-casts]${NC} $1" >&2; exit 1; }

# Check dependencies
command -v jq >/dev/null 2>&1 || err "jq is required"
command -v curl >/dev/null 2>&1 || err "curl is required"

# Check config
[[ -f "$CONFIG_FILE" ]] || err "Config file not found: $CONFIG_FILE"

REFRESH_TOKEN=$(jq -r '.refreshToken' "$CONFIG_FILE")
[[ -n "$REFRESH_TOKEN" && "$REFRESH_TOKEN" != "null" ]] || err "refreshToken not found in config"

# Args
VIDEO_URL="${1:-}"
CUSTOM_TITLE="${2:-}"

[[ -n "$VIDEO_URL" ]] || err "Usage: $0 <youtube-url> [custom-title]"

# Create temp dir
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Build yt-dlp args
YTDLP_ARGS=()
if [[ -f "$COOKIES_FILE" ]]; then
    log "Using cookies file: $COOKIES_FILE"
    YTDLP_ARGS+=(--cookies "$COOKIES_FILE")
fi

# Step 1: Download video
log "Downloading video..."

# Use yt-dlp to get info first
VIDEO_INFO=$(uvx yt-dlp "${YTDLP_ARGS[@]}" --print "%(title)s|||%(id)s" "$VIDEO_URL" 2>/dev/null) || {
    warn "Failed to get video info. YouTube may require cookies."
    warn "Export cookies from your browser using a browser extension like 'Get cookies.txt LOCALLY'"
    warn "Save the file as: $COOKIES_FILE"
    err "Download failed"
}
VIDEO_TITLE=$(echo "$VIDEO_INFO" | cut -d'|' -f1)
VIDEO_ID=$(echo "$VIDEO_INFO" | rev | cut -d'|' -f1 | rev)

# Use custom title if provided
if [[ -n "$CUSTOM_TITLE" ]]; then
    FINAL_TITLE="$CUSTOM_TITLE"
else
    FINAL_TITLE="$VIDEO_TITLE"
fi

log "Title: $FINAL_TITLE"

# Download with sanitized filename
OUTPUT_FILE="$TEMP_DIR/${VIDEO_ID}.mp4"
uvx yt-dlp "${YTDLP_ARGS[@]}" "$VIDEO_URL" --remux-video mp4 -o "$OUTPUT_FILE" --no-playlist || err "Failed to download video"

[[ -f "$OUTPUT_FILE" ]] || err "Downloaded file not found"

FILE_SIZE=$(stat -c%s "$OUTPUT_FILE")
log "Downloaded: $(numfmt --to=iec-i --suffix=B $FILE_SIZE)"

# Step 2: Refresh access token
log "Refreshing access token..."

TOKEN_RESPONSE=$(curl -s 'https://api.pocketcasts.com/user/token' \
  -H 'accept: */*' \
  -H 'content-type: application/json' \
  -H 'origin: https://pocketcasts.com' \
  -H 'referer: https://pocketcasts.com/' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' \
  --data-raw "{\"grantType\":\"refresh_token\",\"refreshToken\":\"$REFRESH_TOKEN\"}")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.accessToken')
[[ -n "$ACCESS_TOKEN" && "$ACCESS_TOKEN" != "null" ]] || err "Failed to get access token: $TOKEN_RESPONSE"

log "Got access token"

# Step 3: Request upload URL
log "Requesting upload URL..."

# Sanitize title for JSON
SAFE_TITLE=$(echo "$FINAL_TITLE" | sed 's/"/\\"/g' | sed "s/'/\\'/g")
UPLOAD_TITLE="${SAFE_TITLE}.mp4"

UPLOAD_REQUEST=$(curl -s 'https://api.pocketcasts.com/files/upload/request' \
  -H 'accept: */*' \
  -H "authorization: Bearer $ACCESS_TOKEN" \
  -H 'content-type: application/json' \
  -H 'origin: https://pocketcasts.com' \
  -H 'referer: https://pocketcasts.com/' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36' \
  --data-raw "{\"title\":\"$UPLOAD_TITLE\",\"size\":$FILE_SIZE,\"contentType\":\"video/mp4\",\"hasCustomImage\":false}")

UPLOAD_URL=$(echo "$UPLOAD_REQUEST" | jq -r '.url')
FILE_UUID=$(echo "$UPLOAD_REQUEST" | jq -r '.uuid')

[[ -n "$UPLOAD_URL" && "$UPLOAD_URL" != "null" ]] || err "Failed to get upload URL: $UPLOAD_REQUEST"

log "Got upload URL for file: $FILE_UUID"

# Step 4: Upload to S3
log "Uploading to Pocket Casts (this may take a while)..."

# The URL comes with escaped unicode, jq handles that
HTTP_CODE=$(curl -s -w "%{http_code}" -o /tmp/pc-upload-response.txt \
  -X PUT \
  -H "Content-Type: video/mp4" \
  -T "$OUTPUT_FILE" \
  "$UPLOAD_URL")

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    log "Upload successful! (HTTP $HTTP_CODE)"
else
    err "Upload failed with HTTP $HTTP_CODE: $(cat /tmp/pc-upload-response.txt)"
fi

# Step 5: Cleanup
log "Cleaning up..."
rm -f "$OUTPUT_FILE"
rm -f /tmp/pc-upload-response.txt

echo ""
log "✅ Done! '$FINAL_TITLE' is now in your Pocket Casts Files"
log "UUID: $FILE_UUID"
