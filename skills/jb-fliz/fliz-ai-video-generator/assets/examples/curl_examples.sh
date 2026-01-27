#!/bin/bash
# ============================================================
# Fliz API cURL Examples
# ============================================================
# 
# Replace YOUR_API_KEY with your actual API key from:
# https://app.fliz.ai/api-keys
#
# Usage: Export your API key first:
#   export FLIZ_API_KEY="your-key-here"
#
# Then run individual commands or source this file.
# ============================================================

API_KEY="${FLIZ_API_KEY:-YOUR_API_KEY}"
BASE_URL="https://app.fliz.ai"

# ============================================================
# 1. TEST CONNECTION
# ============================================================
# Verify API key by fetching voices list

echo "Testing connection..."
curl -s -X GET "${BASE_URL}/api/rest/voices" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" | head -c 200

echo -e "\n"

# ============================================================
# 2. CREATE VIDEO (Minimal)
# ============================================================
# Create a video with minimum required parameters

echo "Creating video (minimal)..."
curl -s -X POST "${BASE_URL}/api/rest/video" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "fliz_video_create_input": {
      "name": "My Test Video",
      "description": "This is the full content that will be transformed into a video. The AI will generate a script, images, and voiceover based on this text.",
      "format": "size_16_9",
      "lang": "en"
    }
  }'

echo -e "\n"

# ============================================================
# 3. CREATE VIDEO (Full Options)
# ============================================================
# Create a video with all customization options

echo "Creating video (full options)..."
curl -s -X POST "${BASE_URL}/api/rest/video" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "fliz_video_create_input": {
      "name": "Customized Video",
      "description": "Your complete article or content goes here. This text will be transformed into an AI-generated video with voiceover, images, and subtitles.",
      "category": "article",
      "format": "size_9_16",
      "lang": "fr",
      "script_style": "news_social_media_style",
      "image_style": "digital_art",
      "caption_style": "animated_background",
      "caption_position": "bottom",
      "caption_font": "montserrat",
      "caption_color": "#FFFFFF",
      "caption_uppercase": false,
      "is_male_voice": false,
      "music_volume": 15,
      "site_url": "https://example.com",
      "site_name": "Example Site",
      "webhook_url": "https://your-webhook.com/fliz",
      "is_automatic": true
    }
  }'

echo -e "\n"

# ============================================================
# 4. GET VIDEO STATUS
# ============================================================
# Check video generation progress

VIDEO_ID="YOUR_VIDEO_UUID_HERE"

echo "Getting video status..."
curl -s -X GET "${BASE_URL}/api/rest/videos/${VIDEO_ID}" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json"

echo -e "\n"

# ============================================================
# 5. LIST VIDEOS
# ============================================================
# Get list of videos with pagination

echo "Listing videos..."
curl -s -X GET "${BASE_URL}/api/rest/videos?limit=10&offset=0" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json"

echo -e "\n"

# ============================================================
# 6. TRANSLATE VIDEO
# ============================================================
# Translate existing video to new language

FROM_VIDEO_ID="YOUR_VIDEO_UUID_HERE"
NEW_LANG="es"

echo "Translating video to ${NEW_LANG}..."
curl -s -X POST "${BASE_URL}/api/rest/videos/${FROM_VIDEO_ID}/translate?new_lang=${NEW_LANG}" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json"

echo -e "\n"

# ============================================================
# 7. DUPLICATE VIDEO
# ============================================================
# Create a copy of existing video

echo "Duplicating video..."
curl -s -X POST "${BASE_URL}/api/rest/videos/${FROM_VIDEO_ID}/duplicate" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json"

echo -e "\n"

# ============================================================
# 8. LIST VOICES
# ============================================================
# Get available text-to-speech voices

echo "Listing voices..."
curl -s -X GET "${BASE_URL}/api/rest/voices" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json"

echo -e "\n"

# ============================================================
# 9. LIST MUSICS
# ============================================================
# Get available background music tracks

echo "Listing music tracks..."
curl -s -X GET "${BASE_URL}/api/rest/musics" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json"

echo -e "\n"

# ============================================================
# 10. POLLING SCRIPT
# ============================================================
# Poll video status until completion

poll_video() {
  local video_id="$1"
  local interval="${2:-15}"
  local max_attempts="${3:-40}"
  
  for i in $(seq 1 $max_attempts); do
    echo "Poll attempt $i/$max_attempts..."
    
    response=$(curl -s -X GET "${BASE_URL}/api/rest/videos/${video_id}" \
      -H "Authorization: Bearer ${API_KEY}" \
      -H "Content-Type: application/json")
    
    step=$(echo "$response" | grep -o '"step":"[^"]*"' | cut -d'"' -f4)
    
    echo "  Status: $step"
    
    if [ "$step" = "complete" ]; then
      url=$(echo "$response" | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
      echo "✅ Video complete!"
      echo "   URL: $url"
      return 0
    fi
    
    if [[ "$step" == *"failed"* ]]; then
      echo "❌ Video failed: $step"
      return 1
    fi
    
    sleep $interval
  done
  
  echo "⏱️ Timeout reached"
  return 1
}

# Usage: poll_video "video-uuid-here" 15 40
