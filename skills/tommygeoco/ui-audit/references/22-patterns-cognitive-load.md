# Patterns: Cognitive Load

Patterns for reducing mental effort and preventing user overwhelm.

---

## What is Cognitive Load?

The mental effort required to process information and make decisions. Working memory is limited. Exceed it, and users struggle.

**Three types:**
1. **Intrinsic** — Complexity of the task itself
2. **Extraneous** — Complexity from poor design
3. **Germane** — Effort spent learning (good complexity)

**Goal:** Minimize extraneous load. Respect intrinsic load. Enable germane load.

---

## Pagination & Infinite Scroll

**What:** Breaking large content sets into manageable chunks.

### Cognitive Load Impact

- **Pagination** — Clear mental boundaries, sense of progress
- **Infinite scroll** — No landmarks, can feel endless
- **Load more** — User-controlled expansion

### When to Use Each

| Pattern | Best For |
|---------|----------|
| **Pagination** | Search results, data tables, e-commerce, SEO-critical pages |
| **Infinite scroll** | Social feeds, discovery browsing, image galleries |
| **Load more** | Balanced approach, when users may want more but need control |

### Implementation Guidelines

**Pagination:**
- 10-50 items per page
- Show total count
- Deep linking support
- Consider "jump to page" for large sets

**Infinite Scroll:**
- Clear loading indicator
- "Back to top" button
- Preserve scroll position on return
- Consider footer accessibility

**Load More:**
- Show count loaded vs. total
- Consistent batch size
- Clear button placement

---

## Steppers & Wizards

**What:** Breaking complex processes into sequential steps.

### Benefits

- **Reduced load** — One step at a time
- **Progress visibility** — Know where you are
- **Confidence** — Clear path to completion
- **Error isolation** — Fix issues step by step

### Psychological Principles

- **Chunking** — Break complexity into parts
- **Goal gradient** — Motivation increases near completion
- **Zeigarnik effect** — Incomplete tasks create engagement

### Implementation Guidelines

**DO:**
- Show all steps upfront (numbered or named)
- Indicate current step clearly
- Allow back navigation (within reason)
- Validate before proceeding
- Save progress (in case of abandonment)
- Show summary/review before final submission

**DON'T:**
- Use for < 3 logical steps (overkill)
- Use for > 7 steps (too daunting)
- Hide step count (anxiety-inducing)
- Require linear completion if not necessary
- Lose user data if they navigate away

### Step Design

| Element | Guideline |
|---------|-----------|
| Step count | 3-7 steps ideal |
| Step names | Action-oriented ("Review" not "Step 3") |
| Progress | Visual indicator (bar, dots, numbers) |
| Validation | Per-step before allowing next |
| Summary | Final review before commit |

---

## Minimalist Navigation

**What:** Reducing navigation options to essential items.

### Benefits

- **Reduced decisions** — Fewer choices = easier choices
- **Faster scanning** — Find items quickly
- **Focus** — Attention on primary actions
- **Cleaner interface** — Less visual noise

### Psychological Principles

- **Hick's Law** — More options = longer decision time
- **Paradox of choice** — Too many options = worse decisions
- **Filtering** — Less to filter through

### Implementation Guidelines

**Primary Navigation:**
- 5-7 items maximum
- Most important items visible
- Group secondary items in "More" or submenus
- Use icons + labels (not just icons)

**Strategies:**
- Priority+ navigation (show what fits, collapse rest)
- Hamburger menu (hide until needed)
- Mega menus (for large sites, used carefully)
- Command palette (power users)

**DON'T:**
- Hide everything behind hamburger on desktop
- Use icons without labels for unfamiliar actions
- Create deep navigation hierarchies
- Change navigation per page without reason

---

## Chunked Lists

**What:** Breaking long lists into visually grouped sections.

### Benefits

- **Scannable** — Headers enable skipping
- **Findable** — Alphabetical, categorical, or chronological grouping
- **Memorable** — Sections aid recall
- **Manageable** — Each section is digestible

### Psychological Principles

- **Chunking** — Groups easier than flat lists
- **Law of Proximity** — Grouped items relate
- **Serial position** — Section headers become anchors

### Implementation Guidelines

**DO:**
- Clear section headers
- Consistent grouping logic
- Sticky headers during scroll (for long sections)
- Empty states per section if needed
- Consider collapsible sections

**DON'T:**
- Create too many sections (defeats purpose)
- Use inconsistent grouping logic
- Make headers look like list items
- Group unrelated items

### Grouping Strategies

| Strategy | Use When |
|----------|----------|
| Alphabetical | Long known lists (contacts, countries) |
| Categorical | Distinct types exist |
| Chronological | Time-based relevance |
| Frequency | Most-used items first |
| Custom | User-defined groups |

---

## Simplified Forms

**What:** Forms designed to minimize cognitive effort.

### Strategies

1. **Reduce fields** — Only ask what's necessary
2. **Smart defaults** — Pre-fill when possible
3. **Progressive disclosure** — Show fields as needed
4. **Inline validation** — Feedback as you go
5. **Logical grouping** — Related fields together

### Implementation Guidelines

**Reduce Fields:**
- Audit every field: "Do we *need* this?"
- Make optional fields truly optional
- Consider progressive profiling (ask over time)
- Derive what you can (city from zip, etc.)

**Smart Defaults:**
- Geo-location for country
- Today's date for date fields
- Most common option pre-selected
- Remember user's previous choices

**Progressive Disclosure:**
- Show advanced fields only when needed
- "Add more details" expand pattern
- Conditional fields based on previous answers

**Inline Validation:**
- Validate on blur (not on every keystroke)
- Clear, specific error messages
- Success indicators for valid fields
- Don't prevent typing valid values

**Field Layout:**
- Single column preferred (easier scanning)
- Labels above fields (faster)
- Consistent field widths
- Adequate spacing between fields

---

## Cognitive Load Reduction Principles

### 1. Eliminate Non-Essential Elements

- Remove purely decorative content
- Hide rarely-used options
- Simplify language
- Reduce color/visual noise

### 2. Leverage Recognition

- Show options, don't require recall
- Use familiar patterns
- Provide examples
- Use icons + labels

### 3. Offload to the System

- Auto-save
- Auto-fill
- Smart suggestions
- Error prevention

### 4. Support Scanning

- Clear headings
- Bullet points
- Visual hierarchy
- Whitespace

### 5. Reduce Decisions

- Smart defaults
- Recommendations
- Limited choices
- Clear primary action

---

## Cognitive Load Audit

| Check | Impact |
|-------|--------|
| ☐ Navigation items < 7 | Decision fatigue |
| ☐ Form fields minimized | Input effort |
| ☐ Smart defaults used | Decision effort |
| ☐ Content chunked | Processing load |
| ☐ Clear visual hierarchy | Scanning effort |
| ☐ Recognition over recall | Memory load |
| ☐ Progressive disclosure used | Initial overwhelm |
| ☐ Consistent patterns | Learning load |
