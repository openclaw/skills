---
name: excalidraw
description: Generate hand-drawn style diagrams, flowcharts, and architecture diagrams as PNG images from Excalidraw JSON
---

# Excalidraw Diagram Generator

Generate beautiful hand-drawn style diagrams rendered as PNG images.

## Workflow

1. **Generate JSON** — Write Excalidraw element array based on what the user wants
2. **Save to file** — Write JSON to `/tmp/<name>.excalidraw`
3. **Render** — `node <skill_dir>/scripts/render.js /tmp/<name>.excalidraw /tmp/<name>.png`
4. **Send** — Send the PNG via message tool with `filePath`

## Quick Reference

```bash
node <skill_dir>/scripts/render.js input.excalidraw output.png
```

## Element Types

| Type | Shape | Key Props |
|------|-------|-----------|
| `rectangle` | Box | x, y, width, height |
| `ellipse` | Oval | x, y, width, height |
| `diamond` | Decision | x, y, width, height |
| `arrow` | Arrow | connects shapes (see Arrow Binding below) |
| `line` | Line | x, y, points: [[0,0],[dx,dy]] |
| `text` | Label | x, y, text, fontSize, fontFamily (1=hand, 2=sans, 3=code) |

### Styling (all shapes)

```json
{
  "strokeColor": "#1e1e1e",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "hachure",
  "strokeWidth": 2,
  "roughness": 1,
  "strokeStyle": "solid"
}
```

**fillStyle**: `hachure` (diagonal lines), `cross-hatch`, `solid`
**roughness**: 0=clean, 1=hand-drawn (default), 2=very sketchy

## Arrow Binding (IMPORTANT)

**Always use `from`/`to` bindings for arrows.** The renderer auto-calculates edge intersection points — no manual coordinate math needed.

### Simple arrow (straight, between two shapes)
```json
{"type":"arrow","id":"a1","from":"box1","to":"box2","strokeColor":"#1e1e1e","strokeWidth":2,"roughness":1}
```
That's it. No x, y, or points needed. The renderer computes start/end at shape edges.

### Multi-segment arrow (routed path with waypoints)
For arrows that need to go around obstacles, use `absolutePoints` with intermediate waypoints:
```json
{
  "type":"arrow","id":"a2","from":"box3","to":"box1",
  "absolutePoints": true,
  "points": [[375,500],[30,500],[30,127],[60,127]],
  "strokeColor":"#1e1e1e","strokeWidth":2,"roughness":1
}
```
- First point = near source shape edge (will snap to actual edge)
- Last point = near target shape edge (will snap to actual edge)
- Middle points = absolute waypoint coordinates for routing

### Arrow labels
Place a separate text element near the arrow midpoint:
```json
{"type":"text","id":"label","x":215,"y":98,"width":85,"height":16,"text":"sends data","fontSize":10,"fontFamily":1,"strokeColor":"#868e96"}
```

### Arrow styles
- `"strokeStyle":"dashed"` — dashed line
- `"startArrowhead": true` — bidirectional arrow

## Template: Flowchart with Bindings

```json
{
  "type": "excalidraw",
  "version": 2,
  "elements": [
    {"type":"rectangle","id":"start","x":150,"y":50,"width":180,"height":60,"strokeColor":"#1e1e1e","backgroundColor":"#b2f2bb","fillStyle":"hachure","strokeWidth":2,"roughness":1},
    {"type":"text","id":"t1","x":200,"y":65,"width":80,"height":30,"text":"Start","fontSize":20,"fontFamily":1,"strokeColor":"#1e1e1e"},

    {"type":"arrow","id":"a1","from":"start","to":"decision","strokeColor":"#1e1e1e","strokeWidth":2,"roughness":1},

    {"type":"diamond","id":"decision","x":140,"y":170,"width":200,"height":120,"strokeColor":"#1e1e1e","backgroundColor":"#ffec99","fillStyle":"hachure","strokeWidth":2,"roughness":1},
    {"type":"text","id":"t2","x":185,"y":215,"width":110,"height":30,"text":"Condition?","fontSize":18,"fontFamily":1,"strokeColor":"#1e1e1e","textAlign":"center"},

    {"type":"arrow","id":"a2","from":"decision","to":"process","strokeColor":"#1e1e1e","strokeWidth":2,"roughness":1},

    {"type":"rectangle","id":"process","x":150,"y":350,"width":180,"height":60,"strokeColor":"#1e1e1e","backgroundColor":"#a5d8ff","fillStyle":"hachure","strokeWidth":2,"roughness":1},
    {"type":"text","id":"t3","x":190,"y":365,"width":100,"height":30,"text":"Process","fontSize":20,"fontFamily":1,"strokeColor":"#1e1e1e"}
  ]
}
```

## Layout Guidelines

- **Node size**: 140-200 × 50-70 px
- **Diamond**: 180-200 × 100-120 px (taller for text)
- **Vertical spacing**: 60-100 px between nodes
- **Horizontal spacing**: 80-120 px between nodes
- **Text**: Position inside shape manually (offset ~15-30px from top-left of shape)
- **Arrow labels**: Place as separate text elements near midpoint of arrow path

## Color Palette

**Fills**: `#a5d8ff` (blue), `#b2f2bb` (green), `#ffec99` (yellow), `#ffc9c9` (red), `#d0bfff` (purple), `#f3d9fa` (pink), `#fff4e6` (cream)
**Strokes**: `#1e1e1e` (dark), `#1971c2` (blue), `#2f9e44` (green), `#e8590c` (orange), `#862e9c` (purple)
**Labels**: `#868e96` (gray, for annotations)

## Tips

- Every element needs a unique `id` (required for binding!)
- Use `from`/`to` on arrows — don't calculate coordinates manually
- `roughness:0` for clean diagrams, `1` for sketchy feel
- Text `fontFamily:1` for hand-drawn, `3` for code
- Group related elements spatially, color-code by type
- For nested layouts, use a large background rectangle as a container
