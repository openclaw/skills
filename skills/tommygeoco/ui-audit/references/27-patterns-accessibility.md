# Patterns: Accessibility

Patterns for ensuring interfaces are usable by everyone.

---

## Why Accessibility Matters

- **Legal** — ADA, Section 508, WCAG compliance requirements
- **Ethical** — Equal access is a design responsibility
- **Business** — 15%+ of users have some disability
- **Quality** — Accessible design improves UX for everyone

**Core principle:** Accessibility is not a checklist item—it's a design approach.

---

## Keyboard Navigation

**What:** Full functionality without a mouse.

### Requirements

| Pattern | Keyboard Support |
|---------|------------------|
| **Focus order** | Tab moves logically through page |
| **Focus visible** | Current focus always visible |
| **Activation** | Enter/Space activates buttons/links |
| **Navigation** | Arrow keys navigate within components |
| **Escape** | Escape closes modals/popups |
| **Shortcuts** | Common shortcuts available |

### Focus Order Principles

1. Follow visual reading order (left-to-right, top-to-bottom)
2. Skip decorative/non-interactive elements
3. Group related controls
4. Don't trap focus (except in modals)
5. Return focus appropriately after interactions

### Implementation Guidelines

**DO:**
- Use semantic HTML (inherits keyboard support)
- Provide visible focus indicators (not outline: none)
- Test with keyboard only
- Support standard keyboard patterns
- Announce changes to screen readers

**DON'T:**
- Use div/span for interactive elements (without ARIA)
- Remove focus outlines without replacement
- Create custom interactions without keyboard support
- Change focus order unpredictably
- Trap users in infinite tab loops

### Focus Indicator Styling

```css
/* Visible, high contrast focus */
:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
}

/* Remove default only when custom is applied */
button:focus {
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.5);
}
```

---

## ARIA Attributes

**What:** Accessible Rich Internet Applications—additional semantics for assistive technology.

### Core ARIA Rules

1. **First rule:** Don't use ARIA if native HTML works
2. **Second rule:** Don't change native semantics
3. **Third rule:** All interactive ARIA must be keyboard accessible
4. **Fourth rule:** Don't use role="presentation" on focusable elements
5. **Fifth rule:** All interactive elements must have accessible names

### Essential ARIA Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `aria-label` | Accessible name | `<button aria-label="Close">×</button>` |
| `aria-describedby` | Additional description | Links to help text |
| `aria-hidden` | Hide from assistive tech | Decorative elements |
| `aria-expanded` | Toggle state | Accordions, dropdowns |
| `aria-selected` | Selection state | Tabs, list items |
| `aria-live` | Announce changes | Dynamic content |
| `aria-invalid` | Invalid state | Form validation |
| `aria-required` | Required field | Form fields |

### Common Patterns

**Button with icon only:**
```html
<button aria-label="Delete item">
  <svg aria-hidden="true">...</svg>
</button>
```

**Accordion:**
```html
<button aria-expanded="false" aria-controls="panel1">
  Section Title
</button>
<div id="panel1" hidden>Content...</div>
```

**Live region:**
```html
<div aria-live="polite" aria-atomic="true">
  <!-- Content changes announced by screen reader -->
</div>
```

---

## Alternative Text

**What:** Text equivalents for non-text content.

### Alt Text Guidelines

**Informative images:**
- Describe the content/function
- Be concise but complete
- Don't include "image of" or "picture of"

**Decorative images:**
- Use empty alt: `alt=""`
- Or use `aria-hidden="true"`

**Functional images (buttons/links):**
- Describe the action, not the image
- "Submit form" not "arrow icon"

**Complex images:**
- Provide detailed description nearby
- Use `aria-describedby` to link
- Consider data tables for charts

### Examples

| Image | Bad Alt | Good Alt |
|-------|---------|----------|
| Logo | "Logo" | "Acme Corp" |
| Search icon | "Magnifying glass" | "Search" |
| Product photo | "Photo" | "Blue cotton t-shirt, front view" |
| Decorative border | "Border" | `alt=""` (empty) |
| Chart | "Chart" | "Sales increased 25% from Q1 to Q2" + full data table |

---

## Color & Contrast

**What:** Ensuring content is perceivable regardless of color vision.

### Contrast Requirements

| Content | Minimum Ratio | Target Ratio |
|---------|---------------|--------------|
| Normal text | 4.5:1 | 7:1 (AAA) |
| Large text (18px+) | 3:1 | 4.5:1 (AAA) |
| UI components | 3:1 | 4.5:1 |
| Focus indicators | 3:1 | 4.5:1 |

### Color Guidelines

**DO:**
- Use high contrast combinations
- Include patterns/icons in addition to color
- Test with color blindness simulators
- Provide color contrast alternatives
- Verify with automated tools

**DON'T:**
- Use color as the only indicator
- Use low contrast text
- Place colored text on similar backgrounds
- Assume everyone sees the same colors
- Use red/green as the only differentiator

### Color + Pattern Example

```
✓ Success (green check icon + green color)
✗ Error (red X icon + red color + border)
! Warning (yellow triangle icon + yellow background)
```

---

## Text & Readability

**What:** Ensuring text is readable by all users.

### Guidelines

**Font size:**
- Minimum 16px for body text
- Support browser zoom up to 200%
- Use relative units (rem, em)

**Line length:**
- 45-75 characters per line
- Max-width on text containers

**Line height:**
- 1.5 minimum for body text
- 1.2 minimum for headings

**Font choice:**
- Sans-serif for UI
- Avoid decorative fonts for body
- Adequate x-height

**Text resizing:**
- Content must remain usable at 200% zoom
- No horizontal scrolling at 320px width

---

## Interactive Elements

**What:** Making interactive elements accessible.

### Minimum Sizes

| Element | Minimum Size | Target Size |
|---------|--------------|-------------|
| Touch targets | 44x44px | 48x48px |
| Click targets | 24x24px | 32x32px |
| Spacing between | 8px | 12px |

### Element Guidelines

**Links:**
- Descriptive text (not "click here")
- Distinguish from regular text
- Show visited state
- Focus + hover states

**Buttons:**
- Clear labels
- Sufficient size
- Visible states (hover, focus, active, disabled)
- Keyboard accessible

**Forms:**
- Labels associated with inputs
- Error messages linked (aria-describedby)
- Required fields indicated
- Group related fields (fieldset/legend)

---

## Motion & Animation

**What:** Respecting user preferences for reduced motion.

### Guidelines

**DO:**
- Respect `prefers-reduced-motion`
- Keep animations subtle
- Allow users to pause/stop animations
- Avoid flashing content (seizure risk)

**DON'T:**
- Auto-play video with motion
- Use fast/flashing animations
- Create vestibular triggers
- Force users to watch animations

### Implementation

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation: none !important;
    transition: none !important;
  }
}
```

---

## Screen Reader Testing

**What:** Verifying experience for screen reader users.

### Testing Checklist

☐ All images have appropriate alt text
☐ Headings create logical outline (H1 → H2 → H3)
☐ Links and buttons have descriptive names
☐ Form labels are associated with inputs
☐ Error messages are announced
☐ Dynamic content changes are announced
☐ Focus management works after interactions
☐ Page title is descriptive

### Screen Readers to Test

- **VoiceOver** — macOS/iOS (built-in)
- **NVDA** — Windows (free)
- **JAWS** — Windows (paid, enterprise standard)
- **TalkBack** — Android (built-in)

---

## Accessibility Checklist

| Category | Requirements |
|----------|--------------|
| ☐ **Keyboard** | All functions keyboard accessible |
| ☐ **Focus** | Visible focus indicators |
| ☐ **Semantics** | Proper HTML elements + ARIA |
| ☐ **Images** | Alt text for all meaningful images |
| ☐ **Color** | Not the only differentiator |
| ☐ **Contrast** | 4.5:1 for text, 3:1 for UI |
| ☐ **Text** | Resizable, readable, proper hierarchy |
| ☐ **Motion** | Reducible, not seizure-inducing |
| ☐ **Forms** | Labels, errors, required indicators |
| ☐ **Testing** | Verified with screen reader |
