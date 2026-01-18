# Information Scaffold: Psychology, Economics, Accessibility, Defaults

Your scaffold = pre-made decisions for recurring situations. Build once, reuse forever.

---

## Design Psychology Reference

Psychological principles categorized by the problem they solve:

### Filtering (Helping users focus)

| Principle | Definition | Application |
|-----------|------------|-------------|
| **Hick's Law** | More options = harder decisions | Reduce choices, progressive disclosure |
| **Law of Proximity** | Close objects perceived as related | Group related items spatially |
| **Law of Similarity** | Visually similar elements perceived as related | Consistent styling for related items |
| **Nudging** | Subtle cues influence behavior | Defaults, visual emphasis, copy |
| **Priming** | Cues influence decision-making | Strategic first impressions, context setting |
| **Progressive Disclosure** | Reveal information gradually | Hide complexity until needed |
| **Tesler's Law** | Complexity must exist somewhere | Absorb complexity in design, not user's head |
| **Von Restorff Effect** | Distinctive items remembered | Make key actions visually distinct |

### Sense-making (Helping users understand)

| Principle | Definition | Application |
|-----------|------------|-------------|
| **Chunking** | Group info into digestible units | Cards, sections, tabs |
| **Cognitive Load Theory** | Working memory is limited | Minimize extraneous info |
| **Jakob's Law** | Users expect your site to work like others | Follow conventions |
| **Law of Common Region** | Fenced objects perceived as related | Use containers, borders |
| **Law of Prägnanz** | Simpler objects easier to process | Reduce visual complexity |
| **Law of Uniform Connectedness** | Connected elements perceived as related | Use lines, shared containers |
| **Occam's Razor** | Prefer simpler explanations | Simplify UI and messaging |
| **Social Proof** | People conform to observed behavior | Testimonials, user counts |

### Efficiency (Helping users act faster)

| Principle | Definition | Application |
|-----------|------------|-------------|
| **Fitt's Law** | Larger, closer targets faster to hit | Size CTAs appropriately, reduce distance |
| **Goal Gradient Effect** | Motivation increases near goal completion | Progress indicators, milestone celebrations |
| **Hyperbolic Discounting** | Immediate rewards valued higher | Quick wins, instant feedback |
| **IKEA Effect** | People value what they helped create | Customization, personalization |
| **Investment Loops** | Engagement increases with investment | Progressive commitment |
| **Pareto Principle** | 80% of effects from 20% of causes | Optimize critical paths |
| **Parkinson's Law** | Work expands to fill time available | Set clear scope, deadlines |
| **Second-Order Effects** | Consequences have consequences | Consider downstream impact |
| **Sunk Cost Effect** | Continued investment despite poor returns | Beware over-commitment |
| **Weber's Law** | Large changes more noticeable | Meaningful differences in UI states |

### Recall (Helping users remember)

| Principle | Definition | Application |
|-----------|------------|-------------|
| **Fresh Start Effect** | Motivation at new beginnings | Leverage time-based resets |
| **Miller's Law** | 7±2 items in short-term memory | Chunk information |
| **Peak-End Rule** | Experiences judged by peak and end | Design strong endings |
| **Picture Superiority Effect** | Images more memorable than text | Use visuals for key info |
| **Serial Position Effect** | First/last items most memorable | Place key items at start/end |
| **Zeigarnik Effect** | Incomplete tasks remembered more | Use incomplete states strategically |

---

## Economics Fundamentals

Design decisions have business implications. Know these concepts:

| Concept | Definition | Design Implication |
|---------|------------|-------------------|
| **Economies of Scale** | More production = lower unit cost | Reusable components pay dividends at scale |
| **Opportunity Cost** | What you give up by choosing | Every design choice excludes alternatives |
| **Time Value of Money** | Money now > money later | Ship valuable features sooner |
| **Supply & Demand** | Scarcity drives price | Exclusive features, limited access can increase perceived value |
| **Zero Marginal Cost** | Digital copies cost nothing extra | Design for scale, not scarcity |
| **Network Effects** | Value increases with users | Prioritize collaboration, sharing features |
| **Diseconomies of Scale** | Too big = inefficient | Complexity costs increase; keep systems manageable |
| **Economies of Scope** | Cheaper to do multiple things together | Shared components across products |
| **Veblen Goods** | Higher price = higher demand (luxury) | Premium positioning affects design choices |
| **Invisible Hand** | Markets self-regulate | User choice will surface winners |

---

## Accessibility Reference (POUR)

WCAG's four principles. Accessibility is not optional.

### Perceivable
- Text alternatives for non-text content
- Captions/transcripts for multimedia
- User can change presentation
- Content easier to see and hear

### Operable
- All functionality accessible via keyboard
- Users have enough time to read/use content
- No seizure-inducing content
- Easy navigation and content finding
- Input modalities beyond keyboard

### Understandable
- Text and UI readable and understandable
- Content operates in predictable ways
- Help users avoid and correct mistakes

### Robust
- Compatible with browsers and assistive tech
- Valid markup

**Minimum baseline:** 4.5:1 contrast ratio for text, focus indicators, alt text, semantic HTML.

---

## Default Typefaces

Choose one neutral sans-serif to start. Add personality later.

**Recommended starting typefaces:**
- Inter
- Nunito Sans
- Mona Sans
- SF Pro (Apple ecosystem)
- Segoe UI (Microsoft ecosystem)

### Default Type Scale

Start with 16px base (browser default). Use this scale:

| Size | Use |
|------|-----|
| 12px | Captions, labels, metadata |
| 14px | Secondary text, descriptions |
| 16px | Body text (base) |
| 18px | Large body, intro text |
| 20px | Small headings |
| 24px | Section headings |
| 30px | Page headings |
| 36px | Feature headings |
| 48px | Hero headings |
| 60px+ | Display text |

---

## Default Design Rules

Establish these defaults to avoid re-deciding:

### Spacing
- Base unit: 8px
- Scale: 4, 8, 12, 16, 24, 32, 48, 64, 96
- Use consistent rhythm

### Colors
- One primary action color
- One or two neutral grays
- Semantic colors: error (red), success (green), warning (yellow), info (blue)
- Ensure contrast ratios

### Icons
Pick one library and stick to it:
- Feather Icons (minimal)
- Heroicons (Tailwind)
- Phosphor Icons (flexible)
- Material Icons (comprehensive)

### Radius
- Consistent border-radius across components
- Common: 4px (subtle), 8px (soft), 16px+ (rounded)

### Shadows/Elevation
- 3-4 levels of elevation
- Consistent shadow direction
- Use for layering, not decoration

---

## Atomic Design Principles

Design systems built on composition:

1. **Atoms** — Basic elements (buttons, inputs, labels)
2. **Molecules** — Simple component groups (search box = input + button)
3. **Organisms** — Complex components (header, card grid)
4. **Templates** — Page layouts without content
5. **Pages** — Templates with real content

Build from small to large. Composition enables reuse.

---

## Nielsen's 10 Usability Heuristics

Quick reference for heuristic evaluation:

1. **Visibility of system status** — Keep users informed
2. **Match between system and real world** — Speak users' language
3. **User control and freedom** — Support undo, exits
4. **Consistency and standards** — Follow conventions
5. **Error prevention** — Prevent problems before they occur
6. **Recognition over recall** — Make options visible
7. **Flexibility and efficiency** — Shortcuts for experts
8. **Aesthetic and minimalist design** — Remove unnecessary elements
9. **Help users recognize, diagnose, recover from errors** — Clear error messages
10. **Help and documentation** — Easy to search, task-focused
