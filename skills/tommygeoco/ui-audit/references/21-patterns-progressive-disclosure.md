# Patterns: Progressive Disclosure

Patterns for revealing information gradually, on demand.

---

## What is Progressive Disclosure?

Showing only the information users need at each moment, with additional details available on demand. Reduces cognitive load while maintaining access to complexity.

**Core principle:** Simple by default, powerful when needed.

---

## Tooltips & Popovers

**What:** Small overlays triggered by hover/focus/tap showing additional context.

### Tooltips vs. Popovers

| Tooltips | Popovers |
|----------|----------|
| Text only | Rich content (images, links, actions) |
| Hover-triggered | Click-triggered usually |
| Auto-dismiss | User dismisses |
| Brief explanation | Detailed information |
| No interaction | Can contain interactions |

### Benefits & Use Cases

- **Explanation** — Clarify icon meanings, abbreviations
- **Guidance** — Inline help without cluttering UI
- **Preview** — Peek at content before committing
- **Details** — Additional info for power users

### Psychological Principles

- **Progressive disclosure** — Detail available when needed
- **Recognition over recall** — Explanation in context
- **Filtering** — Non-essential info hidden until requested

### Implementation Guidelines (Tooltips)

**DO:**
- Delay appearance (300-500ms) to avoid flicker
- Position to not obscure related content
- Keep text brief (1-2 sentences max)
- Provide keyboard access (show on focus)
- Use arrow pointing to trigger element

**DON'T:**
- Use for essential information
- Require tooltips to complete tasks
- Show on touch without alternative (no hover on mobile)
- Put interactive elements in tooltips
- Make them too long to read quickly

### Implementation Guidelines (Popovers)

**DO:**
- Clear close mechanism (X, click outside)
- Appropriate max-width for content
- Position dynamically (flip if near edge)
- Allow interactions within
- Consider mobile-specific behavior (bottom sheets)

**DON'T:**
- Nest popovers within popovers
- Put critical actions only in popovers
- Open on hover (confusing behavior)
- Make too large (use a modal instead)

---

## Nested Menus

**What:** Multi-level dropdown menus for hierarchical navigation.

### Benefits & Use Cases

- **Hierarchy** — Navigate deep category structures
- **Space efficient** — Many options in small trigger
- **Organization** — Group related actions
- **Power users** — Complex command palettes

### Psychological Principles

- **Chunking** — Options grouped logically
- **Progressive disclosure** — Deeper options revealed on demand
- **Hick's Law** — Hierarchy reduces visible choices at each level

### Implementation Guidelines

**DO:**
- Limit nesting depth (2-3 levels max)
- Clear visual indicator for submenus (arrow)
- Appropriate hover delay for submenus (300ms)
- Keep submenus visible while navigating
- Keyboard navigation (arrows to navigate, Enter to select)

**DON'T:**
- Deeply nest menus (hard to navigate)
- Make menus too narrow for content
- Require precise mouse movements
- Hide critical actions in deep nests
- Mix menu types inconsistently

### Positioning Guidelines

- Open toward available space (flip if at edge)
- Submenus open to side with most room
- Consider mobile alternatives (drill-down, bottom sheets)

---

## Expandable Rows

**What:** Table or list rows that expand to reveal details.

### Benefits & Use Cases

- **Overview first** — Scannable summary view
- **Details on demand** — Expand for more
- **In-context** — Details appear near summary
- **Comparison** — Compare multiple expanded rows

### Psychological Principles

- **Progressive disclosure** — Detail when needed
- **Filtering** — Hide details unless requested
- **Recall** — Summary aids memory; details available

### Implementation Guidelines

**DO:**
- Clear expand/collapse indicator
- Smooth animation
- Distinct visual treatment for expanded content
- Allow multiple rows expanded (usually)
- Preserve expanded state during interactions

**DON'T:**
- Auto-collapse other rows (usually—unless space critical)
- Nest expandable rows within expandable rows
- Put primary actions only in expanded view
- Make expanded content too tall (becomes a page)
- Forget keyboard accessibility

### Content in Expanded Rows

- Additional metadata
- Action buttons
- Related items
- Full description
- Inline forms (for edit-in-place)

---

## Drawers & Sheets

**What:** Panels that slide in from screen edge, overlaying content.

### Side Drawers vs. Bottom Sheets

| Side Drawers | Bottom Sheets |
|--------------|---------------|
| Desktop primary | Mobile primary |
| Navigation menus | Actions, options |
| Longer content | Shorter content |
| Wider content | Full-width content |
| Slide from left/right | Slide from bottom |

### Benefits & Use Cases

- **Context preservation** — Main content visible behind
- **Temporary focus** — Complete task then return
- **Space efficient** — Off-screen until needed
- **Navigation** — Mobile nav menus
- **Filters** — Search refinement panels

### Psychological Principles

- **Progressive disclosure** — Reveal when needed
- **Context maintenance** — Don't lose place
- **Filtering** — Focused attention on drawer content

### Implementation Guidelines

**DO:**
- Clear close mechanism (X, tap outside, swipe)
- Appropriate width (280-400px for side drawers)
- Overlay/scrim behind to focus attention
- Animate open/close smoothly
- Trap focus within drawer (accessibility)

**DON'T:**
- Make drawers too wide (becomes a page)
- Put critical info only in drawers
- Stack multiple drawers
- Open automatically without user action
- Forget keyboard users (Escape to close)

### Mobile Considerations

- Bottom sheets generally preferred on mobile
- Allow swipe to dismiss
- Consider detent heights (partial, full)
- Respect safe areas

---

## Modals (Dialogs)

**What:** Overlays that demand attention and require dismissal.

### When to Use Modals

- Require user decision (confirm, choose)
- Critical information that can't be missed
- Focused task (compose, edit)
- Interrupt current flow intentionally

### When NOT to Use Modals

- Showing information (use popover, drawer)
- Non-blocking notifications (use toast)
- Navigation (use page, drawer)
- Error messages (use inline feedback)

### Benefits & Use Cases

- **Focus** — Block other interaction
- **Confirmation** — Prevent accidental actions
- **Interruption** — Force user to acknowledge
- **Isolation** — Complete task before continuing

### Psychological Principles

- **Attention capture** — Demands response
- **Decision forcing** — User must act
- **Context switch** — Clear change of task

### Implementation Guidelines

**DO:**
- Clear title describing the modal purpose
- Primary action prominent (visual emphasis)
- Secondary action available (cancel/back)
- Close via X button AND clicking backdrop AND Escape key
- Focus first interactive element on open
- Return focus to trigger on close

**DON'T:**
- Overuse modals (modal fatigue)
- Stack modals (one modal opening another)
- Require scrolling in modals (usually)
- Use for errors that don't need confirmation
- Auto-open modals without user action
- Disable backdrop click to close (unless destructive action)

### Modal Sizes

| Size | Use Case |
|------|----------|
| Small (400px) | Simple confirmations |
| Medium (600px) | Forms, content preview |
| Large (800px+) | Complex tasks, multi-step |
| Full screen | Immersive tasks (mobile common) |

---

## Read More Links

**What:** Truncated content with option to reveal full text.

### Benefits & Use Cases

- **Overview** — Scannable summaries
- **Choice** — User decides what to read
- **Space efficient** — Long content doesn't dominate
- **SEO-friendly** — Full content in DOM

### Implementation Guidelines

**DO:**
- Natural truncation point (sentence break, not mid-word)
- Clear "Read more" link/button
- Consider inline expansion vs. navigate to full page
- Show character count or reading time for long content
- Animate expansion smoothly

**DON'T:**
- Truncate critically important content
- Use arbitrary truncation lengths (vary by content)
- Truncate to single words ("...")
- Hide the only instance of information
- Make "Read more" the only way to access content

### Truncation Guidelines

| Content Type | Truncation Point |
|--------------|------------------|
| Card descriptions | 2-3 lines |
| Table cells | 1 line with tooltip |
| List item descriptions | 1-2 sentences |
| Blog excerpts | 150-250 characters |

---

## Progressive Disclosure Pattern Selection

| Need | Pattern |
|------|---------|
| Quick explanation | Tooltip |
| Rich preview | Popover |
| Deep navigation | Nested menus |
| Detail on demand (lists) | Expandable rows |
| Temporary panel | Drawer/sheet |
| Required decision | Modal |
| Optional full content | Read more |
