# Patterns: Chunking

Patterns for breaking content into digestible, organized units.

---

## What is Chunking?

Breaking complex information into smaller, manageable pieces that users can process and remember more easily. Based on Miller's Law (7±2 items in working memory).

**Core principle:** Users can't process everything at once. Group related items, separate unrelated items.

---

## Card-Based Layouts

**What:** Contained units of related content with clear boundaries.

### Benefits & Use Cases

- **Scannable** — Users quickly identify relevant cards
- **Self-contained** — Each card is a complete unit
- **Flexible** — Cards work in grids, lists, or carousels
- **Actionable** — Cards can be interactive (click, expand, drag)

### Psychological Principles

- **Law of Common Region** — Boundary creates relatedness
- **Chunking** — Content grouped into digestible units
- **Recognition over recall** — Visual cards easier to scan

### Implementation Guidelines

**DO:**
- Clear visual boundary (border, shadow, or background)
- Consistent card structure across the set
- Visual hierarchy within the card (image → title → description → actions)
- Appropriate sizing for content (not too cramped or empty)
- Interactive states (hover, selected)

**DON'T:**
- Mix card sizes without purpose
- Overload cards with too much content
- Use cards for single items (overkill)
- Nest cards inside cards
- Forget empty states

### Common Variants

| Variant | Use Case |
|---------|----------|
| Media card | Image/video prominent |
| Stat card | Single metric focus |
| Action card | Primary CTA emphasis |
| Profile card | Person/account info |
| Preview card | Summary with expand |

---

## Tabs & Accordions

**What:** Show/hide content sections to reduce visible complexity.

### When to Use Tabs vs. Accordions

| Tabs | Accordions |
|------|------------|
| 2-7 peer sections | Many sections (5+) |
| Mutually exclusive content | Content can stack |
| Horizontal space available | Vertical list format |
| Users need to switch frequently | Users view one at a time |

### Benefits & Use Cases

- **Space efficient** — Show only relevant content
- **User control** — Users choose what to see
- **Progressive disclosure** — Reduce cognitive load
- **Organization** — Clear content categorization

### Psychological Principles

- **Hick's Law** — Fewer visible options = easier decisions
- **Progressive disclosure** — Reveal complexity gradually
- **Miller's Law** — Chunk content into sections

### Implementation Guidelines (Tabs)

**DO:**
- Clear active state
- Limit to 7 tabs (use dropdown for more)
- Descriptive labels (2-3 words)
- Logical order (frequency or process)
- Preserve state when switching

**DON'T:**
- Use tabs for sequential steps (use steppers)
- Mix tabs with different content types
- Use very long labels
- Nest tabs within tabs
- Auto-switch tabs without user action

### Implementation Guidelines (Accordions)

**DO:**
- Clear expand/collapse indicators (chevron, +/-)
- Allow multiple open (usually) or single open (sometimes)
- Animate expansion smoothly
- Keyboard accessible (Enter/Space to toggle)
- Consider default-expanded first item

**DON'T:**
- Nest accordions deeply
- Hide critical information in collapsed sections
- Use vague headers
- Make all sections collapsed by default if users need most of them

---

## Grouped Form Fields

**What:** Related form fields visually grouped together.

### Benefits & Use Cases

- **Scannable** — Related fields easy to locate
- **Logical** — Reflects user mental model
- **Reduced errors** — Related info filled together
- **Progress sense** — Completing groups feels like progress

### Psychological Principles

- **Law of Proximity** — Close items perceived as related
- **Chunking** — Smaller groups easier to process
- **Goal gradient** — Visible progress motivates completion

### Implementation Guidelines

**DO:**
- Group by relationship (personal info, shipping, payment)
- Use visual separation (whitespace, lines, containers)
- Label groups with clear headers
- 3-5 fields per group typically
- Consider two-column layout for short fields

**DON'T:**
- Create groups that are too large
- Separate clearly related fields (first/last name)
- Use inconsistent grouping across forms
- Over-decorate group boundaries

### Common Groupings

| Group | Fields |
|-------|--------|
| Personal | Name, email, phone |
| Address | Street, city, state, zip, country |
| Payment | Card, expiry, CVV, billing address |
| Credentials | Username/email, password, confirm |
| Preferences | Notification settings, privacy |

---

## Pagination

**What:** Breaking large lists into discrete pages.

### Pagination vs. Infinite Scroll vs. Load More

| Pattern | Use When |
|---------|----------|
| **Pagination** | User needs to locate specific items, page numbers meaningful, SEO important |
| **Infinite scroll** | Browsing/discovery, no specific target, continuous consumption (social feeds) |
| **Load more** | Compromise between above, user controls when to load |

### Benefits & Use Cases

- **Orientation** — Users know where they are (page 3 of 10)
- **Shareable** — Deep links to specific pages
- **Performance** — Predictable page loads
- **Completion sense** — Can reach "the end"

### Psychological Principles

- **Chunking** — Content in manageable batches
- **Progress** — Page numbers show advancement
- **Control** — User decides when to load more

### Implementation Guidelines

**DO:**
- Show current page and total pages
- Provide first/last page shortcuts (for many pages)
- Truncate middle pages with ellipsis (1 2 3 ... 10)
- Show items per page (and allow customization)
- Preserve page in URL (deep linking)

**DON'T:**
- Use pagination for < 20 items
- Hide page count
- Break in the middle of logical groups
- Require clicking through many pages for common tasks
- Forget keyboard navigation

### Page Size Guidelines

| Context | Items/Page |
|---------|------------|
| Data tables | 10-50, user configurable |
| Search results | 10-25 |
| Product listings | 12-48 |
| Blog/articles | 5-10 |

---

## Carousels & Sliders

**What:** Horizontal scrollable content, often auto-advancing.

### Benefits & Use Cases

- **Space efficient** — Many items in limited space
- **Visual interest** — Dynamic, engaging
- **Feature highlights** — Hero promotions, featured content
- **Related content** — "You might also like"

### Psychological Principles

- **Curiosity** — Partial visibility entices exploration
- **Chunking** — Subset of content at a time
- **Serial position** — First items get most attention

### Implementation Guidelines

**DO:**
- Show partial next item (indicates more content)
- Clear navigation controls (arrows, dots)
- Allow touch/swipe on mobile
- Consider auto-advance carefully (user control preferred)
- Pause auto-advance on hover/focus

**DON'T:**
- Auto-advance too fast (5+ seconds minimum)
- Use for critical content (users miss it)
- Hide navigation controls
- Use multiple carousels on same page
- Rely on carousel for primary navigation

### Critical Warnings

⚠️ Carousels have notoriously low engagement beyond first item
⚠️ Users often miss carousel content entirely
⚠️ Auto-advance frustrates users trying to read
⚠️ Consider if content is important enough to warrant space without hiding

### Better Alternatives

- Grid of items (all visible)
- Horizontal scroll (user-controlled)
- Featured + list (primary + secondary)
- Accordion (if order matters less)

---

## Chunking Pattern Selection Guide

| User Need | Pattern |
|-----------|---------|
| Compare items | Cards in grid |
| View details on demand | Accordions |
| Switch between categories | Tabs |
| Fill related information | Grouped forms |
| Navigate large sets | Pagination |
| Browse highlights | Carousel (with caution) |
