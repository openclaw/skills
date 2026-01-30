# Reusable JSON Prompt Templates for Nano Banana Pro

This file contains pre-built templates for common product categories. Copy and modify as needed.

---

## Jewelry Templates

### Necklace / Pendant
```json
{
  "subject": {
    "description": "Elegant gold chain necklace with small diamond pendant",
    "pose": "Upper body, looking slightly down to showcase pendant",
    "angle": "Close-up, shallow depth of field",
    "lighting": "Studio lighting, soft highlight on pendant"
  },
  "model": {
    "appearance": "Young adult woman, natural makeup, neat hair",
    "outfit": "Simple black top, high collar to frame necklace",
    "expression": "Gentle smile, eyes looking down at pendant"
  },
  "environment": {
    "background": "Pure white seamless background",
    "location": "Professional studio",
    "atmosphere": "Luxurious, elegant, clean"
  },
  "technical": {
    "style": "Commercial product photography, photorealistic",
    "camera": "Macro lens 100mm, aperture f/2.8",
    "resolution": "1024x1024"
  }
}
```

### Earrings
```json
{
  "subject": {
    "description": "Silver drop earrings with small crystals",
    "pose": "Side profile, earrings clearly visible",
    "angle": "Upper body, slight angle to show both earrings",
    "lighting": "Studio lighting with subtle reflections"
  },
  "model": {
    "appearance": "Young adult woman, hair tied back or styled to show earrings",
    "outfit": "Simple top that contrasts with silver color",
    "expression": "Natural, slight smile"
  },
  "environment": {
    "background": "Pure white seamless background",
    "location": "Professional studio",
    "atmosphere": "Elegant, clean, bright"
  },
  "technical": {
    "style": "Jewelry photography, photorealistic",
    "camera": "85mm portrait lens, sharp focus on earrings",
    "resolution": "1024x1024"
  }
}
```

---

## Fashion Templates

### T-Shirt / Casual Wear
```json
{
  "subject": {
    "description": "White cotton t-shirt with minimalist design",
    "pose": "Full body standing upright, relaxed posture",
    "angle": "Full body, slight angle from front",
    "lighting": "Soft studio lighting, even illumination"
  },
  "model": {
    "appearance": "Young adult, fitness model physique",
    "outfit": "White t-shirt paired with jeans or casual pants",
    "expression": "Confident, approachable smile"
  },
  "environment": {
    "background": "Pure white seamless background",
    "location": "Studio setting with minimal shadows",
    "atmosphere": "Casual, approachable, modern"
  },
  "technical": {
    "style": "Fashion photography, clean commercial aesthetic",
    "camera": "50mm lens, full body framing",
    "resolution": "1024x1024"
  }
}
```

### Dress / Formal Wear
```json
{
  "subject": {
    "description": "Elegant evening dress in deep blue color",
    "pose": "Full body standing, one hand on hip",
    "angle": "Full body, showing dress silhouette",
    "lighting": "Studio lighting with soft shadows to show fabric drape",
    "model": {
      "appearance": "Young adult woman, elegant styling",
      "outfit": "Blue evening dress, matching accessories",
      "expression": "Confident, slightly turned to camera"
    },
    "environment": {
      "background": "Pure white seamless background",
      "location": "Professional studio",
      "atmosphere": "Elegant, sophisticated, premium"
    },
    "technical": {
      "style": "High fashion photography, photorealistic",
      "camera": "85mm lens, elegant framing",
      "resolution": "1024x1024"
    }
  }
}
```

---

## Accessory Templates

### Phone Case
```json
{
  "subject": {
    "description": "Designer phone case with geometric pattern",
    "pose": "Hand holding phone naturally, thumb on screen",
    "angle": "Close-up, focus on case design",
    "lighting": "Studio lighting, soft shadows on hand"
  },
  "model": {
    "appearance": "Young adult hand, well-manicured nails",
    "outfit": "Simple casual clothing to not distract",
    "expression": "N/A (focus on hand)"
  },
  "environment": {
    "background": "Pure white seamless background",
    "location": "Product photography studio",
    "atmosphere": "Clean, focused, detail-oriented"
  },
  "technical": {
    "style": "Macro product photography, sharp details",
    "camera": "Macro lens, shallow depth of field",
    "resolution": "1024x1024"
  }
}
```

### Watch
```json
{
  "subject": {
    "description": "Minimalist stainless steel watch",
    "pose": "Wrist clearly visible, watch face showing",
    "angle": "Close-up, focus on watch face and band",
    "lighting": "Studio lighting with subtle reflections on metal"
  },
  "model": {
    "appearance": "Young adult, clean look",
    "outfit": "Business casual shirt to complement watch",
    "expression": "N/A (focus on wrist)"
  },
  "environment": {
    "background": "Pure white seamless background",
    "location": "Product photography studio",
    "atmosphere": "Professional, premium, clean"
  },
  "technical": {
    "style": "Product photography, sharp metal details",
    "camera": "Macro lens, precise focus",
    "resolution": "1024x1024"
  }
}
```

---

## Cosmetics Templates

### Lipstick
```json
{
  "subject": {
    "description": "Luxury red lipstick in gold tube",
    "pose": "Product in hand or resting on surface",
    "angle": "Close-up macro shot",
    "lighting": "Studio lighting with soft highlights on gold cap"
  },
  "model": {
    "appearance": "Young adult hand, neat manicure",
    "outfit": "Simple clothing, neutral colors",
    "expression": "N/A (product focus)"
  },
  "environment": {
    "background": "Pure white seamless background",
    "location": "Cosmetics photography studio",
    "atmosphere": "Luxurious, glamorous, clean"
  },
  "technical": {
    "style": "Cosmetic product photography, photorealistic",
    "camera": "Macro lens, sharp details",
    "resolution": "1024x1024"
  }
}
```

---

## Animation Prompts for Veo/Kling

### Subtle Natural Movement
- "Gentle body sway, arms naturally moving, breathing motion"
- "Slow head movement, slight smile change, relaxed posture"
- "Small hand gesture highlighting product, natural flow"

### Product Showcase
- "Model turning slightly to show product from different angles"
- "Hand gently touching product, drawing attention to features"
- "Slight forward lean, product in clear view"

### Dynamic (for fashion)
- "Natural walking motion, arms gently swinging"
- "Turn and pause, showing full outfit"
- "Shoulder movement, fabric flowing naturally"

### Close-up (for jewelry/accessories)
- "Subtle hand movement, catching light on metal/jewelry"
- "Wrist rotation, showing watch from multiple angles"
- "Gentle head movement, earring moving naturally with hair"

---

## Tips for Template Customization

### Product Descriptions
- Be specific: "gold necklace" vs "elegant gold chain necklace with diamond pendant"
- Include features: "minimalist design", "geometric pattern", "classic style"
- Mention materials: "stainless steel", "silver", "gold-plated"

### Pose Selection
Match pose to product:
- **Jewelry**: Upper body, focus on neck/wrist/hands
- **Fashion**: Full body, showing silhouette and flow
- **Accessories**: Close-up, macro shots for details

### Lighting Adjustments
- **Metal jewelry**: Studio lighting with soft reflections
- **Fashion**: Even lighting, show fabric texture
- **Cosmetics**: Soft highlights on premium materials

### Model Appearance
- Target audience demographics
- Brand aesthetic (young, mature, professional, casual)
- Product complement (outfit should not clash)

---

## Template Usage Workflow

1. Copy relevant template above
2. Replace `description` with your product
3. Adjust `pose` to match Pinterest reference
4. Modify `model` to fit your target audience
5. Update `lighting` for desired mood
6. Test in Nano Banana Pro
7. Iterate based on results
