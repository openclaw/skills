# Patterns: Onboarding

Patterns for introducing users to your product and helping them reach value quickly.

---

## What is Onboarding?

The process of helping new users understand and succeed with your product. Goal: Get users to their "aha moment" as fast as possible.

**Core principle:** Onboarding isn't about teaching features—it's about delivering value.

---

## Product Tours

**What:** Guided walkthroughs highlighting key features.

### Types

| Type | Best For |
|------|----------|
| **Linear tour** | Simple products, sequential workflows |
| **Spotlight tour** | Complex products, key features only |
| **Interactive tour** | Learning by doing |
| **Video tour** | Complex concepts, emotional connection |

### Implementation Guidelines

**DO:**
- Keep it short (3-5 steps max)
- Focus on value, not features
- Allow skipping
- Make it contextual (trigger at right moment)
- Test completion rates

**DON'T:**
- Force users to complete tour
- Cover every feature
- Block user from exploring
- Repeat tour without consent
- Show tour to returning users

### Tour Step Anatomy

```
[Highlight area]

Step 2 of 4

Create your first project
Click here to start building. Projects 
organize your work and team collaboration.

[Got it] [Skip tour]

● ● ○ ○ (progress dots)
```

---

## Contextual Tips

**What:** Help that appears when and where relevant.

### Types

| Type | Trigger | Example |
|------|---------|---------|
| **Tooltips** | Hover/focus | Icon explanations |
| **Coach marks** | First visit to area | Feature introduction |
| **Hotspots** | Available anytime | Pulsing indicator for help |
| **Inline hints** | Contextual | Empty state guidance |

### Implementation Guidelines

**DO:**
- Appear at point of need
- Dismiss after shown once (usually)
- Focus on one thing at a time
- Be genuinely helpful
- Allow users to re-access tips

**DON'T:**
- Interrupt user workflows
- Show too many at once
- Repeat dismissed tips
- Block interaction
- State the obvious

### Contextual Tip Timing

| Trigger | When to Show |
|---------|--------------|
| First visit | User reaches feature for first time |
| Feature discovery | User hovers/focuses on new element |
| Error recovery | User makes mistake, offer guidance |
| Idle state | User seems stuck |
| Feature release | New feature for existing users |

---

## Interactive Tutorials

**What:** Learning by doing within the product.

### Benefits

- **Active learning** — More effective than passive
- **Real context** — Learning in actual interface
- **Immediate value** — Complete real tasks
- **Verification** — Confirm understanding

### Implementation Guidelines

**DO:**
- Use real product, not simulated
- Start with high-value task
- Provide clear success criteria
- Celebrate completion
- Allow exploration

**DON'T:**
- Create fake practice environments
- Make tutorials too long
- Prevent users from deviating
- Penalize mistakes
- Make completion mandatory

### Interactive Tutorial Structure

```
1. Introduction (why this matters)
2. Task instruction (what to do)
3. Action (user does the thing)
4. Confirmation (success feedback)
5. Context (what else you can do)
```

---

## Checklists

**What:** Progress trackers for setup or learning.

### Benefits

- **Clear progress** — Sense of advancement
- **Motivation** — Goal gradient effect
- **Structure** — Know what's next
- **Completion drive** — Zeigarnik effect

### Implementation Guidelines

**DO:**
- Start with easy wins (first items)
- Show progress percentage
- Celebrate completions
- Make items actionable (link to action)
- Allow dismissal

**DON'T:**
- Include too many items (5-7 max)
- Make all items mandatory
- Reset progress
- Hide the checklist
- Nag about incomplete items

### Checklist UI Pattern

```
Get Started with [Product]
━━━━━━━━━━░░░░░░ 60% complete

✓ Create your account
✓ Add your first project
✓ Invite a team member
○ Connect your calendar
○ Set your preferences

[Continue →]

[Dismiss for now]
```

---

## Empty States

**What:** Onboarding when there's no content yet.

### Empty State as Onboarding

| State | Opportunity |
|-------|-------------|
| No projects | "Create your first project" |
| No data | "Import your existing data" |
| No connections | "Connect your tools" |
| No team | "Invite your team" |

### Implementation Guidelines

**DO:**
- Explain what goes here
- Provide clear CTA to populate
- Show what it will look like (sample data)
- Offer templates/presets
- Be encouraging

**DON'T:**
- Leave completely empty
- Use generic "No data" messages
- Assume user knows what to do
- Hide the empty state help
- Make user feel lost

### Empty State Anatomy

```
[Illustration]

No projects yet

Projects help you organize your work and 
collaborate with your team.

[Create your first project]

or [Start with a template]
```

---

## Progressive Onboarding

**What:** Spreading onboarding over time vs. all at once.

### Approach

| Time | Onboarding Focus |
|------|------------------|
| **Signup** | Absolute minimum (email, password) |
| **First session** | Core value action only |
| **Second session** | Secondary features |
| **First week** | Deeper functionality |
| **Ongoing** | Advanced features, tips |

### Implementation Guidelines

**DO:**
- Front-load value, not setup
- Introduce features when relevant
- Remember what's been shown
- Personalize based on behavior
- Celebrate milestones

**DON'T:**
- Dump everything at once
- Show irrelevant features
- Repeat already-learned content
- Ignore user progress
- Rush to "completion"

### Progressive Disclosure Example

```
Day 1: "Create your first [X]"
Day 3: "You've created 3 projects! Try organizing with folders."
Day 7: "Ready for advanced filters? Here's a quick tip."
Day 14: "Power user tip: keyboard shortcuts"
```

---

## Onboarding for Different Users

### By User Type

| User Type | Onboarding Approach |
|-----------|---------------------|
| **New to category** | Concept education + product tour |
| **Experienced user** | Skip basics, highlight differentiators |
| **Returning user** | Show what's new |
| **Invited user** | Context about who invited and why |

### Segmented Onboarding

```
[During signup or first run]

What brings you here today?

○ I'm exploring [category] for the first time
○ I'm switching from another tool
○ I was invited by my team
○ Just browsing

[Continue]
```

---

## Measuring Onboarding Success

### Key Metrics

| Metric | What it Tells You |
|--------|-------------------|
| **Activation rate** | % reaching first value moment |
| **Time to value** | How long to reach aha moment |
| **Tour completion** | % completing onboarding steps |
| **Drop-off points** | Where users abandon |
| **Feature adoption** | Which features stick |

### Optimization

1. Define your activation event (what = success?)
2. Measure current baseline
3. Identify friction points
4. Test improvements
5. Monitor retention correlation

---

## Onboarding Anti-Patterns

| Anti-Pattern | Problem |
|--------------|---------|
| **Tour torture** | Forced, unskippable 15-step tour |
| **Sign-up interrogation** | 10 fields before seeing product |
| **Feature vomit** | Explaining everything at once |
| **Permanent tooltips** | Tips that never go away |
| **Guilt tripping** | "You haven't completed setup!" |
| **Fake progress** | Progress bars that reset |
| **No escape** | Can't use product without tutorial |

---

## Onboarding Checklist

| Element | Implemented? |
|---------|--------------|
| ☐ Clear value proposition upfront | |
| ☐ Minimal signup friction | |
| ☐ First-run experience designed | |
| ☐ Empty states guide action | |
| ☐ Contextual tips available | |
| ☐ Progress indicators visible | |
| ☐ Tours skippable | |
| ☐ Success celebrations | |
| ☐ Measuring activation | |
