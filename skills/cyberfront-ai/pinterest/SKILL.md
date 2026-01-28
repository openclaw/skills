---
name: pinterest
description: Search and browse Pinterest pins, get pin details, and send actual images to the user via Telegram/messaging. Use when the user wants to find inspiration, search for images/ideas, or browse Pinterest content. Sends images directly, not just links.
---

# Pinterest Skill

Search, browse, and share Pinterest pins — sends actual images to chat, not just links.

## Quick Search & Send Images

### Step 1: Search Pinterest
```
browser action=navigate url="https://www.pinterest.com/search/pins/?q=YOUR+SEARCH+TERMS"
browser action=snapshot
```

### Step 2: Get High-Res Image URLs
From the snapshot, find image URLs. Pinterest images follow this pattern:
- Thumbnail: `https://i.pinimg.com/236x/...`
- Medium: `https://i.pinimg.com/564x/...`
- **High-res: `https://i.pinimg.com/originals/...`**

To get high-res: replace `236x` or `564x` with `originals` in the URL.

### Step 3: Send Images to User
**Send actual image (not link!):**
```
message action=send media="https://i.pinimg.com/originals/xx/xx/image.jpg" message="Pin description here"
```

**Send multiple images:**
```
message action=send media="https://i.pinimg.com/originals/..." message="Option 1: Modern minimal"
message action=send media="https://i.pinimg.com/originals/..." message="Option 2: Cozy rustic"
```

## Detailed Pin Workflow

1. **Navigate** to Pinterest search
2. **Snapshot** to see results
3. **Click** on a pin for details (gets larger image)
4. **Screenshot** the pin detail page OR extract originals URL
5. **Send image** via message tool with `media=` parameter

### Getting Original Images
When on a pin detail page:
- Look for `<img>` with `src` containing `i.pinimg.com`
- Convert to originals: `https://i.pinimg.com/originals/{hash}.jpg`

## Example: "Find me minimalist desk setups"

```
# 1. Search
browser action=navigate url="https://www.pinterest.com/search/pins/?q=minimalist+desk+setup"
browser action=snapshot

# 2. Extract image URLs from snapshot (look for i.pinimg.com)
# 3. Convert to high-res originals

# 4. Send images
message action=send media="https://i.pinimg.com/originals/ab/cd/ef123.jpg" message="Clean white desk with plant 🌿"
message action=send media="https://i.pinimg.com/originals/gh/ij/kl456.jpg" message="Wooden desk, natural light ☀️"
```

## Alternative: Screenshot Method

If image URL extraction is tricky, screenshot the pin:
```
browser action=navigate url="https://www.pinterest.com/pin/123456/"
browser action=screenshot
# Then send the screenshot file
message action=send filePath="/path/to/screenshot.jpg" message="Here's the pin!"
```

## API Method (For User's Own Content)

Requires OAuth token setup — see `references/oauth-setup.md`

```bash
export PINTEREST_ACCESS_TOKEN="your_token"
python3 scripts/pinterest_api.py boards
python3 scripts/pinterest_api.py board-pins <board_id>
python3 scripts/pinterest_api.py pin <pin_id>
```

## Key Points

- ✅ **Always send images directly** using `media=` parameter
- ✅ Use `originals` URLs for high-res
- ❌ Don't just send links — send the actual image
- 💡 If URL doesn't work, screenshot the pin and send that

## References

- OAuth setup: `references/oauth-setup.md`
- API endpoints: `references/api-reference.md`
