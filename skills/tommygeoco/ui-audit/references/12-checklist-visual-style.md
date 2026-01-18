# Checklist: Improving Visual Style

Systematic checks for visual design consistency and quality.

---

## Spacing

Consistent rhythm creates visual harmony.

### Spacing System

☐ **Base unit defined** — Usually 4px or 8px
☐ **Scale established** — e.g., 4, 8, 12, 16, 24, 32, 48, 64
☐ **Consistent application** — Same spacing for same relationships

### Spacing Types

☐ **Padding** — Space inside containers
☐ **Margin** — Space between elements
☐ **Gap** — Space in flex/grid layouts
☐ **Gutters** — Space between columns

### Spacing Relationships

☐ **Related items closer** — Law of Proximity
☐ **Unrelated items farther** — Visual grouping
☐ **Hierarchy through spacing** — More space = more importance
☐ **Breathing room** — Adequate whitespace

### Common Issues

- Inconsistent spacing between similar elements
- Too little whitespace (cramped)
- Too much whitespace (disconnected)
- Padding/margin not on the spacing scale

---

## Colors

Color communicates meaning and creates hierarchy.

### Color System

☐ **Primary color** — Brand/action color
☐ **Secondary color** — Supporting accent
☐ **Neutral palette** — Grays for text, backgrounds, borders
☐ **Semantic colors** — Error, success, warning, info

### Color Usage

☐ **Text colors** — Primary, secondary, disabled, placeholder
☐ **Background colors** — Surface hierarchy (elevated, base, sunken)
☐ **Border colors** — Default, focus, error
☐ **Interactive states** — Hover, active, focus variations

### Color Accessibility

☐ **Contrast ratios** — 4.5:1 for normal text, 3:1 for large text
☐ **Not color alone** — Don't rely solely on color to convey info
☐ **Color blindness** — Test with simulators
☐ **Dark mode** — Colors work in both modes

### Common Issues

- Too many colors (lack of cohesion)
- Insufficient contrast
- Inconsistent semantic usage (different reds for errors)
- Color used as only differentiator

---

## Elevation

Visual layers create depth and hierarchy.

### Elevation Levels

☐ **Level 0** — Base surface (no shadow)
☐ **Level 1** — Slight elevation (cards, sections)
☐ **Level 2** — Moderate elevation (dropdowns, popovers)
☐ **Level 3** — High elevation (modals, dialogs)
☐ **Level 4** — Highest elevation (toasts, tooltips above modals)

### Shadow Properties

☐ **Consistent direction** — Light source consistent
☐ **Blur radius** — Increases with elevation
☐ **Spread** — Usually minimal
☐ **Opacity** — Decreases with distance
☐ **Color** — Usually dark gray/black, can be colored

### Elevation Usage

☐ **Interactive elements** — Buttons may elevate on hover
☐ **Overlay content** — Modals, drawers clearly elevated
☐ **Sticky elements** — Headers/navs elevated when scrolling
☐ **Focus indication** — Can supplement or replace outlines

### Common Issues

- Inconsistent shadow direction
- Too many elevation levels
- Shadows too harsh or too subtle
- Elevation doesn't match interaction hierarchy

---

## Iconography

Icons support comprehension and reduce text.

### Icon System

☐ **Single icon library** — Consistent style
☐ **Consistent stroke/fill** — Don't mix styles
☐ **Size scale** — 16, 20, 24, 32, 48 (or similar)
☐ **Consistent grid** — Icons align to same grid

### Icon Usage

☐ **With text labels** — For unclear icons
☐ **Standalone** — Only for universally understood (close, search, home)
☐ **In buttons** — Left or right of text consistently
☐ **In navigation** — Supplement text, not replace
☐ **As status** — Error, success, warning indicators

### Icon Accessibility

☐ **Alt text/aria-label** — For meaningful icons
☐ **aria-hidden** — For decorative icons
☐ **Touch targets** — 44x44px minimum for tappable icons
☐ **Color contrast** — Icons meet contrast requirements

### Common Issues

- Mixed icon styles (outline + filled)
- Icons without labels where meaning unclear
- Inconsistent icon sizes
- Too many unique icons

---

## Typography

Text is the primary interface. Make it work.

### Type Scale

☐ **Scale established** — Limited set of sizes (7-10)
☐ **Consistent usage** — Same size for same purpose
☐ **Responsive scaling** — Appropriate for device

### Type Hierarchy

☐ **H1-H6** — Clear heading hierarchy
☐ **Body text** — Primary and secondary
☐ **Captions/labels** — Small supporting text
☐ **Display text** — Hero/feature text

### Type Properties

☐ **Line height** — 1.4-1.6 for body, 1.1-1.3 for headings
☐ **Letter spacing** — Adjusted for size (tighter large, looser small)
☐ **Font weight** — 2-3 weights max
☐ **Max line length** — 45-75 characters for readability

### Type Accessibility

☐ **Minimum size** — 16px for body text
☐ **Contrast** — 4.5:1 ratio
☐ **Scalability** — Works when user zooms
☐ **Font choice** — Legible at small sizes

### Common Issues

- Too many font sizes
- Inconsistent line heights
- Lines too long (hard to read)
- Insufficient contrast on secondary text

---

## Imagery & Illustrations

Visual content enhances understanding and tone.

### Image Usage

☐ **Consistent style** — Photography style or illustration style
☐ **Appropriate aspect ratios** — Consistent crops
☐ **Quality** — High resolution, appropriate compression
☐ **Relevance** — Images support content, not decorate

### Image Treatments

☐ **Placeholders** — Loading states for images
☐ **Error states** — Broken image handling
☐ **Cropping** — Consistent crop ratios
☐ **Filters/overlays** — Consistent treatment

### Image Accessibility

☐ **Alt text** — Descriptive for meaningful images
☐ **Empty alt** — For decorative images
☐ **Text in images** — Avoided or duplicated in HTML
☐ **Color contrast** — Text over images readable

### Illustration Guidelines

☐ **Consistent style** — Same illustrator or style guide
☐ **Color palette** — Within brand colors
☐ **Stroke weights** — Consistent with icons
☐ **Character design** — If using people, consistent representation

---

## Motion & Animation

Movement creates meaning and delight.

### Animation Purposes

☐ **Feedback** — Response to user action
☐ **Orientation** — Help users understand spatial relationships
☐ **Attention** — Draw focus to important changes
☐ **Continuity** — Smooth transitions between states

### Animation Properties

☐ **Duration** — 100-500ms typical (faster = less important)
☐ **Easing** — Ease-out for entrances, ease-in for exits
☐ **Consistency** — Same duration for same type of animation
☐ **Purpose** — Every animation has a reason

### Animation Best Practices

☐ **Prefer transforms** — translate, scale, rotate, opacity (performant)
☐ **Avoid layout thrash** — Don't animate width, height, position
☐ **Reduce motion** — Respect prefers-reduced-motion
☐ **Subtlety** — Most animations should be barely noticed

### Common Issues

- Animations too slow (feel sluggish)
- Animations too fast (miss the feedback)
- Gratuitous animation (no purpose)
- Inconsistent easing/duration
- Ignoring accessibility preferences

---

## Texture & Patterns

Surface treatments add depth and character.

### Texture Types

☐ **Subtle gradients** — Add depth without distraction
☐ **Background patterns** — Subtle, non-distracting
☐ **Noise/grain** — Adds warmth to flat colors
☐ **Glass effects** — Blur, transparency (use sparingly)

### Usage Guidelines

☐ **Subtlety** — Textures shouldn't compete with content
☐ **Purpose** — Differentiate surfaces, add depth
☐ **Consistency** — Same treatment for same surface type
☐ **Performance** — Consider render cost

### Common Issues

- Textures too prominent
- Inconsistent texture usage
- Performance impact from complex textures
- Reduced legibility from background patterns

---

## Visual Style Audit

Quick checks for visual consistency:

| Element | ✓ | Notes |
|---------|---|-------|
| Spacing on scale | | |
| Color palette limited | | |
| Contrast accessible | | |
| Elevation consistent | | |
| Single icon style | | |
| Type scale limited | | |
| Line heights consistent | | |
| Images consistent style | | |
| Animations purposeful | | |
| Reduced motion respected | | |
