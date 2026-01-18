---
name: ui-audit
description: "AI skill for automated UI audits. Evaluate interfaces against proven UX principles for visual hierarchy, accessibility, cognitive load, navigation, and more. Based on Making UX Decisions by Tommy Geoco."
author: Tommy Geoco
homepage: https://audit.uxtools.co
logo: logo-light.png
logoDark: logo-dark.png
---

# UI Audit Skill

Evaluate interfaces against proven UX principles. Based on [Making UX Decisions](https://uxdecisions.com) by Tommy Geoco.

## When to Use This Skill

- Making UI/UX design decisions under time pressure
- Evaluating design trade-offs with business context
- Choosing appropriate UI patterns for specific problems
- Reviewing designs for completeness and quality
- Structuring design thinking for new interfaces

## Core Philosophy

**Speed ≠ Recklessness.** Designing quickly is not automatically reckless. Recklessly designing quickly is reckless. The difference is intentionality.

## The 3 Pillars of Warp-Speed Decisioning

1. **Scaffolding** — Rules you use to automate recurring decisions
2. **Decisioning** — Process you use for making new decisions  
3. **Crafting** — Checklists you use for executing decisions

## Quick Reference Structure

### Foundational Frameworks
- `references/00-core-framework.md` — 3 pillars, decisioning workflow, macro bets
- `references/01-anchors.md` — 7 foundational mindsets for design resilience
- `references/02-information-scaffold.md` — Psychology, economics, accessibility, defaults

### Checklists (Execution)
- `references/10-checklist-new-interfaces.md` — 6-step process for designing new interfaces
- `references/11-checklist-fidelity.md` — Component states, interactions, scalability, feedback
- `references/12-checklist-visual-style.md` — Spacing, color, elevation, typography, motion
- `references/13-checklist-innovation.md` — 5 levels of originality spectrum

### Patterns (Reusable Solutions)
- `references/20-patterns-chunking.md` — Cards, tabs, accordions, pagination, carousels
- `references/21-patterns-progressive-disclosure.md` — Tooltips, popovers, drawers, modals
- `references/22-patterns-cognitive-load.md` — Steppers, wizards, minimalist nav, simplified forms
- `references/23-patterns-visual-hierarchy.md` — Typography, color, whitespace, size, proximity
- `references/24-patterns-social-proof.md` — Testimonials, UGC, badges, social integration
- `references/25-patterns-feedback.md` — Progress bars, notifications, validation, contextual help
- `references/26-patterns-error-handling.md` — Form validation, undo/redo, dialogs, autosave
- `references/27-patterns-accessibility.md` — Keyboard nav, ARIA, alt text, contrast, zoom
- `references/28-patterns-personalization.md` — Dashboards, adaptive content, preferences, l10n
- `references/29-patterns-onboarding.md` — Tours, contextual tips, tutorials, checklists
- `references/30-patterns-information.md` — Breadcrumbs, sitemaps, tagging, faceted search
- `references/31-patterns-navigation.md` — Priority nav, off-canvas, sticky, bottom nav

## Usage Instructions

### For Design Decisions
1. Read `00-core-framework.md` for the decisioning workflow
2. Identify if this is a recurring decision (use scaffold) or new decision (use process)
3. Apply the 3-step weighing: institutional knowledge → user familiarity → research

### For New Interfaces
1. Follow the 6-step checklist in `10-checklist-new-interfaces.md`
2. Reference relevant pattern files for specific UI components
3. Use fidelity and visual style checklists to enhance quality

### For Pattern Selection
1. Identify the core problem (chunking, disclosure, cognitive load, etc.)
2. Load the relevant pattern reference
3. Evaluate benefits, use cases, psychological principles, and implementation guidelines

## Decision Workflow Summary

When facing a UI decision:

```
1. WEIGH INFORMATION
   ├─ What does institutional knowledge say? (existing patterns, brand, tech constraints)
   ├─ What are users familiar with? (conventions, competitor patterns)
   └─ What does research say? (user testing, analytics, studies)

2. NARROW OPTIONS
   ├─ Eliminate what conflicts with constraints
   ├─ Prioritize what aligns with macro bets
   └─ Choose based on JTBD support

3. EXECUTE
   └─ Apply relevant checklist + patterns
```

## Macro Bet Categories

Companies win through one or more of:

| Bet | Description | Design Implication |
|-----|-------------|-------------------|
| **Velocity** | Features to market faster | Reuse patterns, find metaphors in other markets |
| **Efficiency** | Manage waste better | Design systems, reduce WIP |
| **Accuracy** | Be right more often | Stronger research, instrumentation |
| **Innovation** | Discover untapped potential | Novel patterns, cross-domain inspiration |

Always align micro design bets with company macro bets.

## Key Principle: Good Design Decisions Are Relative

A design decision is "good" when it:
- Supports the product's jobs-to-be-done
- Aligns with company macro bets
- Respects constraints (time, tech, team)
- Balances user familiarity with differentiation needs

There is no universally correct UI solution—only contextually appropriate ones.

---

## Generating Audit Reports

When asked to audit a design, generate a comprehensive report. Always include these sections:

### Required Sections (always include)
1. **Visual Hierarchy** — Headings, CTAs, grouping, reading flow, type scale, color hierarchy, whitespace
2. **Visual Style** — Spacing consistency, color usage, elevation/depth, typography, motion/animation
3. **Accessibility** — Keyboard navigation, focus states, contrast ratios, screen reader support, touch targets

### Contextual Sections (include when relevant)
4. **Navigation** — For multi-page apps: wayfinding, breadcrumbs, menu structure, information architecture
5. **Usability** — For interactive flows: discoverability, feedback, error handling, cognitive load
6. **Onboarding** — For new user experiences: first-run, tutorials, progressive disclosure
7. **Social Proof** — For landing/marketing pages: testimonials, trust signals, social integration
8. **Forms** — For data entry: labels, validation, error messages, field types

### Audit Output Format

```json
{
  "title": "Design Name — Screen/Flow",
  "project": "Project Name",
  "date": "YYYY-MM-DD",
  "figma_url": "optional",
  "screenshot_url": "optional - URL to screenshot",
  
  "macro_bets": [
    { "category": "velocity|efficiency|accuracy|innovation", "description": "...", "alignment": "strong|moderate|weak" }
  ],
  
  "jtbd": [
    { "user": "User Type", "situation": "context without 'When'", "motivation": "goal without 'I want to'", "outcome": "benefit without 'so I can'" }
  ],
  
  "visual_hierarchy": {
    "title": "Visual Hierarchy",
    "checks": [
      { "label": "Check name", "status": "pass|warn|fail|na", "notes": "Details" }
    ]
  },
  "visual_style": { ... },
  "accessibility": { ... },
  
  "priority_fixes": [
    { "rank": 1, "title": "Fix title", "description": "What and why", "framework_reference": "XX-filename.md → Section Name" }
  ],
  
  "notes": "Optional overall observations"
}
```

### Checks Per Section (aim for 6-10 each)

**Visual Hierarchy**: heading distinction, primary action clarity, grouping/proximity, reading flow, type scale, color hierarchy, whitespace usage, visual weight balance

**Visual Style**: spacing consistency, color palette adherence, elevation/shadows, typography system, border/radius consistency, icon style, motion principles

**Accessibility**: keyboard operability, visible focus, color contrast (4.5:1), touch targets (44px), alt text, semantic markup, reduced motion support

**Navigation**: clear current location, predictable menu behavior, breadcrumb presence, search accessibility, mobile navigation pattern

**Usability**: feature discoverability, feedback on actions, error prevention, recovery options, cognitive load management, loading states
