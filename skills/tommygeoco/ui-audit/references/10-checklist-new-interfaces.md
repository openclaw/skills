# Checklist: Designing New Interfaces

A 6-step process for approaching any new interface from scratch.

---

## Step 1: Define the System

Understand the technical and contextual landscape before designing.

### Key Questions

☐ **What type of system is this?**
- Web application — Cross-platform, easy updates, limited hardware access
- Mobile app — Native performance, deep device integration, separate iOS/Android
- Desktop software — Full processing power, deep system access, requires updates
- Embedded system — Fixed hardware, task-specific, constrained resources

☐ **What are the platform constraints?**
- Screen sizes and orientations
- Input methods (touch, mouse, keyboard, voice)
- Performance requirements
- Offline capabilities needed?

☐ **What data inputs/outputs exist?**
- How do users get data in?
- How do users get data out?
- What integrations are required?

### Best Practices
- Match the system type to user needs and contexts
- Consider browser extensions, mobile companions for web apps
- Prioritize input methods that fit user context

---

## Step 2: Model User Tasks

Define who users are and what they need to accomplish.

### Key Questions

☐ **Who are the different user types?**
- What roles exist?
- What permissions should each role have?
- What are their distinct needs?

☐ **What are primary tasks users need to accomplish?**
- What are the jobs-to-be-done?
- How do tasks break into step-by-step workflows?
- What are entry points, decision points, and endpoints?

☐ **How will users CRUD data?**
- Create, Read, Update, Delete flows
- Necessary sequencing and granularity
- Bulk operations needed?

☐ **What are key data entities?**
- What objects do users interact with?
- How are entities related? (1:1, 1:many, many:many)
- What's the data model?

### Best Practices
- Focus on most frequent and important tasks first
- Use simple, clear language for task descriptions
- Validate task models with user research or feedback
- Label buttons with actions ("Add Content" not "Submit")

---

## Step 3: Organize Information

Structure content and navigation before visual design.

### Key Questions

☐ **What are the high-level categories/sections?**
- Main content areas or features?
- How can categories be logically grouped?

☐ **What are relationships and hierarchies?**
- What's the hierarchy of importance?
- Which entities relate to which? (1:many, many:many)

☐ **What are primary and secondary navigation patterns?**
- Main nav menu structure?
- Contextual or in-page nav needed?
- Breadcrumbs? Secondary nav?

☐ **What content and actions should be prioritized?**
- What info is critical for task completion?
- How can visual hierarchy guide users?

### Best Practices
- Use card sorting or tree testing to validate IA
- Follow established conventions for nav
- Provide clear labels and signposts
- Use breadcrumbs for deep hierarchies

---

## Step 4: Gather Design Inspiration

Research before creating. Stand on shoulders of giants.

### Choose Your Originality Level

1. **Direct copies** — Replicate existing patterns exactly (fastest, least differentiation)
2. **Remixes** — Combine elements from multiple sources
3. **Indirect parallels** — Inspiration from different domains solving similar problems
4. **Metaphors/analogies** — Real-world concepts informing design
5. **True innovation** — New patterns from first principles (slowest, highest risk)

### Inspiration Sources

**Standard:**
- Dribbble, Behance, Awwwards, Pinterest

**More interesting:**
- ProductHunt — How startups differentiate
- Layers.to — Higher quality than Dribbble
- Pageflows.com — User flows of popular apps
- Mobbin.com — Mobile pattern library
- Teardowns.ai — AI feature patterns

### Best Practices
- Focus on examples matching your project constraints
- Look beyond direct competitors to adjacent domains
- Create moodboards and organized collections
- Annotate what works and what doesn't

---

## Step 5: Generate Rapid Ideas

Quantity before quality. Explore widely before refining.

### Key Activities

☐ **Sketch 6+ low-fidelity concepts**
- Don't judge while creating
- Set a timer (15-30 min)
- Explore diverse approaches

☐ **Vary the fundamentals**
- Different layouts
- Different navigation approaches
- Different information hierarchies
- Different interaction patterns

☐ **Focus on structure, not style**
- Boxes and labels, not colors and fonts
- Workflow and flow, not polish

### Idea Generation Techniques

- **Crazy 8s** — 8 ideas in 8 minutes
- **Worst possible idea** — Then invert
- **How would [X company] do this?** — Steal mental models
- **Analogy mapping** — How does [unrelated domain] solve this?
- **Constraint removal** — What if we had no [budget/time/tech] limits?

### Best Practices
- Timebox ideation to prevent overthinking
- Don't fall in love with first idea
- Involve others for diverse perspectives
- Compare against JTBD to evaluate

---

## Step 6: Enhance Fidelity

Move from concept to detailed design.

### Fidelity Progression

1. **Wireframes** — Structure and layout
2. **Low-fi mockups** — Basic styling, real content
3. **High-fi mockups** — Full visual design
4. **Interactive prototypes** — Testable flows

### Key Questions for Enhancement

☐ **Are all component states defined?**
- Default, hover, active, focus, disabled, loading, error

☐ **Are all interactions specified?**
- Primary interactions (clicks, taps)
- Secondary interactions (hovers, long-press)
- Gestures and shortcuts

☐ **Is content scalability addressed?**
- Empty states
- Minimal content
- Maximum/overflow content
- Edge cases

☐ **Is system feedback clear?**
- Loading states
- Success/error feedback
- Progress indicators

☐ **Is user input handled?**
- Validation states
- Error messages
- Help text

☐ **Is navigation complete?**
- All pages/views connected
- Back navigation
- Deep linking

### Best Practices
- Apply fidelity checklists (see 11-checklist-fidelity.md)
- Apply visual style checklists (see 12-checklist-visual-style.md)
- Test with real content, not lorem ipsum
- Review against JTBD and macro bets

---

## Quick Reference: 6-Step Summary

| Step | Focus | Output |
|------|-------|--------|
| 1. Define System | Platform, constraints, data | System requirements doc |
| 2. Model Tasks | Users, workflows, entities | Task flows, CRUD maps |
| 3. Organize Info | Categories, hierarchy, nav | Information architecture |
| 4. Gather Inspiration | Research, patterns, references | Moodboard, pattern library |
| 5. Generate Ideas | Divergent exploration | 6+ wireframe concepts |
| 6. Enhance Fidelity | Detail, polish, edge cases | High-fi designs, prototypes |

**Rule:** Resist the urge to skip to Step 6. Steps 1-5 make Step 6 dramatically faster and better.
