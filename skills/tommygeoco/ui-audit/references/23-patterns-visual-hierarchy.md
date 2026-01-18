# Patterns: Visual Hierarchy

Patterns for guiding attention and creating clear content structure.

---

## What is Visual Hierarchy?

The arrangement of elements to show relative importance. Users should instantly understand what's most important without reading everything.

**Core principle:** Design tells users where to look. Make it intentional.

---

## Typography Hierarchy

**What:** Using type size, weight, and style to establish importance.

### Hierarchy Levels

| Level | Purpose | Typical Treatment |
|-------|---------|-------------------|
| **Display** | Hero content, page title | Largest, boldest |
| **H1** | Page heading | Large, bold |
| **H2** | Section heading | Medium-large, semibold |
| **H3** | Subsection | Medium, semibold |
| **Body** | Primary content | Base size, regular |
| **Secondary** | Supporting text | Smaller, lighter color |
| **Caption** | Labels, metadata | Smallest, light |

### Implementation Guidelines

**DO:**
- 2:1 ratio minimum between heading levels
- Consistent application across pages
- Weight AND size differences (not just one)
- Appropriate line height per level
- Limit to 4-5 distinct levels

**DON'T:**
- Use more than 2 typefaces
- Make headings barely bigger than body
- Use color alone for hierarchy
- Skip heading levels (H1 → H3)
- Use all caps for long text

### Type Scale Example

```
Display:  48px / Bold
H1:       36px / Bold  
H2:       24px / Semibold
H3:       20px / Semibold
Body:     16px / Regular
Small:    14px / Regular
Caption:  12px / Regular
```

---

## Color Hierarchy

**What:** Using color intensity, saturation, and contrast to direct attention.

### Hierarchy Through Color

| Element | Color Treatment |
|---------|-----------------|
| Primary action | Brand color, high saturation |
| Secondary action | Muted/outline variant |
| Primary text | Darkest (near black) |
| Secondary text | Medium gray |
| Disabled | Light gray |
| Destructive | Red family |
| Success | Green family |

### Implementation Guidelines

**DO:**
- High contrast for primary elements
- Reserve saturated colors for actions/emphasis
- Use color consistently (same action = same color)
- Ensure 4.5:1 contrast ratio minimum
- Test with color blindness simulators

**DON'T:**
- Use more than 3-4 colors for UI elements
- Use red for non-destructive actions
- Rely on color alone to convey meaning
- Make secondary elements more colorful than primary
- Use low contrast for important elements

### Color Application

```
Primary action:    Blue-600 (saturated)
Secondary action:  Blue-100 bg + Blue-700 text
Tertiary action:   Gray-200 bg + Gray-800 text
Disabled:          Gray-100 bg + Gray-400 text
```

---

## Whitespace Hierarchy

**What:** Using space to group related items and separate unrelated ones.

### Principles

- More space between unrelated items
- Less space between related items
- Space increases with hierarchy level
- Consistent spacing scale throughout

### Spacing Scale

```
4px   - Tight (icon + label)
8px   - Related elements
16px  - Related groups
24px  - Section spacing
32px  - Major section breaks
48px+ - Page-level separation
```

### Implementation Guidelines

**DO:**
- Follow Law of Proximity religiously
- Use consistent spacing scale
- More space above headings than below
- Generous margins at page level
- Space proportional to importance

**DON'T:**
- Use arbitrary spacing values
- Cram elements together
- Use equal spacing everywhere
- Separate clearly related items
- Waste space inconsistently

---

## Size Hierarchy

**What:** Using element size to indicate importance.

### Size Principles

- Larger = more important
- Primary actions larger than secondary
- Main content larger than supporting
- Size differences should be noticeable (1.5x minimum)

### Button Size Example

```
Large:   48px height (primary page actions)
Medium:  40px height (standard actions)
Small:   32px height (inline/secondary)
X-Small: 24px height (compact contexts)
```

### Card Size Hierarchy

| Purpose | Size |
|---------|------|
| Featured | Largest, spans multiple columns |
| Primary | Standard size, prominent |
| Secondary | Smaller, supporting content |
| Compact | Minimal, high-density contexts |

---

## Proximity & Grouping

**What:** Using spatial relationships to show content relationships.

### The 4 Gestalt Laws for Hierarchy

1. **Proximity** — Close items are related
2. **Similarity** — Similar items are related
3. **Common Region** — Items in same container are related
4. **Connectedness** — Items connected by lines are related

### Application Examples

**Proximity:**
- Form label + input (tight spacing)
- Form group + next group (more spacing)
- Card content grouped tightly
- Cards separated from each other

**Similarity:**
- All navigation items styled the same
- All buttons of same importance styled the same
- All card components share style

**Common Region:**
- Related items in same card/container
- Form fields in fieldset
- Related actions in button group

**Connectedness:**
- Breadcrumbs connected by separators
- Stepper stages connected by line
- Related items connected by visual element

---

## Contrast Hierarchy

**What:** Using contrast differences to establish visual priority.

### Contrast Types

| Type | Application |
|------|-------------|
| **Color contrast** | Light/dark, saturated/muted |
| **Size contrast** | Large/small |
| **Weight contrast** | Bold/regular |
| **Density contrast** | Busy/sparse areas |
| **Motion contrast** | Static/animated |

### Creating Focus

**High contrast for:**
- Primary CTAs
- Important information
- Error states
- Current/active states

**Low contrast for:**
- Secondary actions
- Supporting text
- Disabled states
- Background elements

---

## Position Hierarchy

**What:** Leveraging natural reading patterns and expectations.

### Reading Patterns

**F-Pattern (text-heavy pages):**
- Users scan horizontally at top
- Then vertically down left side
- Place key content along the F

**Z-Pattern (sparse pages):**
- Users scan top left to right
- Then diagonally to bottom left
- Then across bottom
- Place CTAs at end of Z

**Gutenberg Diagram:**
- Top left: Primary optical area (high attention)
- Top right: Strong fallow area
- Bottom left: Weak fallow area  
- Bottom right: Terminal area (natural end, place CTAs)

### Position Guidelines

**DO:**
- Most important content top-left
- Primary actions top-right or bottom-right
- Navigation where expected (top, left)
- CTAs at natural stopping points

**DON'T:**
- Bury primary actions bottom-left
- Place important info in weak fallow area
- Violate expectations without reason
- Scatter actions unpredictably

---

## Hierarchy Patterns by Component

### Cards

1. **Image/media** — Visual hook, top
2. **Title** — Primary info, prominent
3. **Description** — Supporting context
4. **Metadata** — Secondary info, muted
5. **Actions** — Clear CTA, bottom

### Tables

1. **Header row** — Bold, sticky
2. **Key column** — Left-most, often linked
3. **Data columns** — Clear alignment
4. **Actions column** — Right side
5. **Pagination** — Below, muted

### Forms

1. **Form title** — Clear purpose
2. **Section headers** — Group labels
3. **Labels** — Above fields, clear
4. **Inputs** — Prominent
5. **Help text** — Below fields, muted
6. **Primary action** — Emphasized
7. **Secondary action** — De-emphasized

### Pages

1. **Page title** — Clear orientation
2. **Primary content** — Center/prominent
3. **Supporting content** — Secondary/sidebar
4. **Navigation** — Consistent location
5. **Actions** — Contextual, accessible

---

## Hierarchy Audit

| Element | Clear Hierarchy? |
|---------|------------------|
| ☐ Headings distinct from body | |
| ☐ Primary action obvious | |
| ☐ Related items grouped | |
| ☐ Unrelated items separated | |
| ☐ Reading flow logical | |
| ☐ Most important content prominent | |
| ☐ Consistent hierarchy across pages | |
