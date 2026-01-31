# Excalidraw Element Schema Reference

## Common Properties (all elements)

| Property | Type | Required | Default | Notes |
|----------|------|----------|---------|-------|
| `id` | string | yes | — | Unique identifier |
| `type` | string | yes | — | Element type (see below) |
| `x` | number | yes | — | X position (top-left) |
| `y` | number | yes | — | Y position (top-left) |
| `width` | number | yes* | — | *Not for arrow/line |
| `height` | number | yes* | — | *Not for arrow/line |
| `strokeColor` | string | no | `"#1e1e1e"` | CSS color |
| `backgroundColor` | string | no | `"transparent"` | Fill color |
| `fillStyle` | string | no | `"hachure"` | `hachure`, `cross-hatch`, `solid` |
| `strokeWidth` | number | no | `2` | Line thickness |
| `strokeStyle` | string | no | `"solid"` | `solid`, `dashed`, `dotted` |
| `roughness` | number | no | `1` | 0=smooth, 1=normal, 2=very rough |
| `opacity` | number | no | `100` | 0-100 |
| `angle` | number | no | `0` | Rotation in radians |
| `seed` | number | no | random | Roughjs seed for consistent look |

## Element Types

### `rectangle`
Standard box. Use `width` and `height`.

### `ellipse`
Oval/circle. `width`/`height` define the bounding box.

### `diamond`
Diamond/rhombus shape (for decision nodes). `width`/`height` define bounding box.

### `text`
| Property | Type | Default | Notes |
|----------|------|---------|-------|
| `text` | string | — | The text content (use `\n` for multiline) |
| `fontSize` | number | `20` | Font size in px |
| `fontFamily` | number | `1` | 1=Virgil (hand), 2=Helvetica, 3=Cascadia (code) |
| `textAlign` | string | `"left"` | `left`, `center`, `right` |
| `verticalAlign` | string | `"top"` | `top`, `middle` |

### `arrow`
| Property | Type | Notes |
|----------|------|-------|
| `points` | `[[x,y],...]` | Array of [dx,dy] offsets from element x,y |
| `startArrowhead` | string\|null | `"arrow"` or null |
| `endArrowhead` | string\|null | Default: `"arrow"` for type arrow |

Arrow points are **relative** to the element's `x,y`. Example: an arrow from (100,100) going right 200px and down 50px:
```json
{"type":"arrow","x":100,"y":100,"points":[[0,0],[200,50]]}
```

### `line`
Same as arrow but no arrowheads. Uses `points` array.

### `freedraw`
Freehand drawing. Uses `points` array of [dx,dy] offsets.

## Colors Cheat Sheet

### Stroke Colors
- `#1e1e1e` — Black (default)
- `#e03131` — Red
- `#2f9e44` — Green
- `#1971c2` — Blue
- `#f08c00` — Orange
- `#6741d9` — Purple

### Background Colors
- `#a5d8ff` — Light blue
- `#b2f2bb` — Light green
- `#ffec99` — Light yellow
- `#ffc9c9` — Light red/pink
- `#d0bfff` — Light purple
- `#ffd8a8` — Light orange
- `#e9ecef` — Light gray
- `"transparent"` — No fill

## Layout Tips

- Standard node size: 160-200w × 60-80h
- Spacing between nodes: 80-120px
- Arrow length: matches spacing
- Diamond decisions: 180-200w × 100-120h (needs more height)
- Text inside shapes: offset x+20~40, y+15~25 from shape origin
- For centered text in a shape: set `textAlign:"center"` and position text at shape center
