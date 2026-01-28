#!/bin/bash

echo "[ComfyAI] Initializing..." >&2

# Config
COMFY_URL="http://192.168.31.7:8000"
WORKFLOW_FILE="$(pwd)/image_flux2_klein_image_edit_4b_distilled.json"
INPUT_DIR="$(pwd)/input"
OUTPUT_DIR="$(pwd)/output"

# Create required directories
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

# Check if ComfyUI is reachable
curl -s "$COMFY_URL/system_stats" > /dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: ComfyUI not reachable at $COMFY_URL" >&2
    exit 1
fi

# Check if workflow exists
if [ ! -f "$WORKFLOW_FILE" ]; then
    echo "ERROR: Workflow file not found at $WORKFLOW_FILE" >&2
    exit 1
fi

# Read prompt from first argument (text-only case)
PROMPT="$1"
IMAGE_PATH=""

# If a media attachment is provided (image upload), extract its path
if [ -n "$2" ] && [ -f "$2" ]; then
    IMAGE_PATH="$2"
fi

# Load workflow template
TEMP_WORKFLOW="$(mktemp)"
cat "$WORKFLOW_FILE" > "$TEMP_WORKFLOW"

# Handle image-to-image: replace reference image path and update inputs
if [ -n "$IMAGE_PATH" ] && [ -f "$IMAGE_PATH" ]; then
    echo "[ComfyAI] Image-to-image mode: editing $IMAGE_PATH with prompt: $PROMPT" >&2
    
    # Copy uploaded image to skill's input folder (for ComfyUI to load)
    IMAGE_NAME="$(basename "$IMAGE_PATH")"
    cp "$IMAGE_PATH" "$INPUT_DIR/$IMAGE_NAME" 2>/dev/null
    
    # Update the LoadImage node (ID: 76) to use this image
    jq --arg img "$IMAGE_NAME" '.["76"].inputs.image = $img' "$TEMP_WORKFLOW" > "${TEMP_WORKFLOW}.tmp" && mv "${TEMP_WORKFLOW}.tmp" "$TEMP_WORKFLOW"
    
    # Update the positive prompt (ID: 92:74)
    jq --arg txt "$PROMPT" '.["92:74"].inputs.text = $txt' "$TEMP_WORKFLOW" > "${TEMP_WORKFLOW}.tmp" && mv "${TEMP_WORKFLOW}.tmp" "$TEMP_WORKFLOW"
    
else
    # Text-to-image mode: use empty latent + prompt only
    echo "[ComfyAI] Text-to-image mode: generating from prompt: $PROMPT" >&2
    
    # Update the positive prompt (ID: 92:74)
    jq --arg txt "$PROMPT" '.["92:74"].inputs.text = $txt' "$TEMP_WORKFLOW" > "${TEMP_WORKFLOW}.tmp" && mv "${TEMP_WORKFLOW}.tmp" "$TEMP_WORKFLOW"
    
    # Clear any reference image inputs
    jq '.["76"].inputs.image = ""' "$TEMP_WORKFLOW" > "${TEMP_WORKFLOW}.tmp" && mv "${TEMP_WORKFLOW}.tmp" "$TEMP_WORKFLOW"
fi

# Send to ComfyUI API
echo "[ComfyAI] Sending workflow to ComfyUI..." >&2
RESPONSE=$(curl -s -X POST "$COMFY_URL/prompt" \
  -H "Content-Type: application/json" \
  -d "@${TEMP_WORKFLOW}")

# Extract prompt_id
PROMPT_ID=$(echo "$RESPONSE" | jq -r ".prompt_id")
if [ "$PROMPT_ID" = "null" ]; then
    echo "ERROR: Failed to get prompt_id from ComfyUI" >&2
    echo "$RESPONSE" >&2
    exit 1
fi
echo "[ComfyAI] Generated prompt_id: $PROMPT_ID" >&2

# Poll for result (max 60s)
IMAGE_FILENAME=""
for i in {1..30}; do
    sleep 2
    echo "[ComfyAI] Checking status... ($i/30)" >&2
    HISTORY=$(curl -s "$COMFY_URL/history/$PROMPT_ID")
    
    # Check if any output has images
    if echo "$HISTORY" | jq -e '.[].outputs[] | has("images")' > /dev/null; then
        IMAGE_FILENAME=$(echo "$HISTORY" | jq -r '.[].outputs[] | .images[0].filename')
        if [ -n "$IMAGE_FILENAME" ]; then
            break
        fi
    fi
done

if [ -z "$IMAGE_FILENAME" ]; then
    echo "ERROR: Image generation timed out after 60s" >&2
    exit 1
fi

# Construct full output path (ComfyUI saves to its own output folder)
IMAGE_FULL_PATH="$HOME/Desktop/$IMAGE_FILENAME"

# Copy generated image from ComfyUI output to desktop (as requested)
cp "$HOME/ComfyUI/output/$IMAGE_FILENAME" "$IMAGE_FULL_PATH" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERROR: Generated image not found in ComfyUI output folder at ~/ComfyUI/output/$IMAGE_FILENAME" >&2
    exit 1
fi

echo "[ComfyAI] Image saved to desktop: $IMAGE_FULL_PATH" >&2

# Output MEDIA path for Clawdbot to send (desktop file)
echo "MEDIA:$IMAGE_FULL_PATH"