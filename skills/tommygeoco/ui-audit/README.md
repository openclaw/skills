<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="logo-dark.png" />
    <source media="(prefers-color-scheme: light)" srcset="logo-light.png" />
    <img src="logo-light.png" alt="UI Audit" width="50" />
  </picture>
</p>

<p align="center">
  <strong>AI skill for automated UI audits</strong><br>
  Evaluate interfaces against proven UX principles.
</p>

<p align="center">
  <a href="https://audit.uxtools.co">Guidelines</a> •
  <a href="https://clawdhub.com/skills/ui-audit">ClawdHub</a> •
  <a href="https://npmjs.com/package/ui-audit">npm</a>
</p>

---

## What is this?

A skill that gives AI assistants the ability to perform structured UI audits. Based on [Making UX Decisions](https://uxdecisions.com) by Tommy Geoco.

**Audits include:**
- Visual hierarchy & typography
- Visual style & spacing
- Accessibility & contrast
- Navigation & wayfinding
- Cognitive load & information architecture
- Social proof & trust signals
- Onboarding & empty states

## Installation

```bash
# Agent Skills (Vercel)
npx skills add uxtools/ui-audit

# ClawdHub
clawdhub install ui-audit

# npm
npm install ui-audit
```

## Usage

Ask your AI assistant:

```
Audit this design: [figma-url]
Review this landing page for accessibility issues
What visual hierarchy patterns should I use for a pricing page?
```

## What's Included

```
ui-audit/
├── SKILL.md                    # Main skill instructions
├── CLAUDE.md                   # Claude-specific quick reference
└── references/
    ├── 00-core-framework.md    # Decision-making process
    ├── 10-checklist-*.md       # Execution checklists
    └── 2*-patterns-*.md        # UI pattern libraries
```

## Guidelines

View the full list of principles at **[audit.uxtools.co](https://audit.uxtools.co)**

### Decisioning
- Weigh information in order: Institutional knowledge → User familiarity → Research
- Align every decision with macro bets: Velocity, Efficiency, Accuracy, or Innovation
- Define jobs-to-be-done first

### Visual Hierarchy
- Primary action is obvious within 3 seconds
- 2:1 ratio minimum between heading levels
- Related items are grouped (Law of Proximity)

### Accessibility
- Keyboard works everywhere
- Focus is always visible
- Color is not the only indicator

[View all guidelines →](https://audit.uxtools.co)

## Author

**[Tommy Geoco](https://x.com/designertom)** — [uxtools.co](https://uxtools.co) • [uxdecisions.com](https://uxdecisions.com)

## License

MIT
