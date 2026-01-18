# Patterns: Personalization

Patterns for adapting interfaces to individual users.

---

## What is Personalization?

Tailoring the interface, content, or functionality based on user data, preferences, or behavior. The goal is relevance—showing users what matters to them.

**Spectrum:**
- **Customization** — User explicitly sets preferences
- **Personalization** — System adapts based on data/behavior

---

## Customizable Dashboards

**What:** User-configured layouts and widgets.

### Benefits

- **Relevance** — Users see what matters to them
- **Ownership** — IKEA effect (they built it)
- **Efficiency** — Quick access to frequent needs

### Implementation Guidelines

**DO:**
- Provide useful defaults (don't start empty)
- Make customization discoverable but not required
- Allow adding, removing, rearranging widgets
- Save preferences across sessions
- Offer presets/templates

**DON'T:**
- Require customization to use the product
- Make defaults unusable
- Overwhelm with options
- Reset customization without warning
- Hide the reset/restore option

### Widget Patterns

| Pattern | Use For |
|---------|---------|
| **Drag-and-drop** | Rearranging layout |
| **Widget picker** | Adding new widgets |
| **Resize handles** | Adjusting widget size |
| **Edit mode** | Toggled customization state |
| **Templates** | Starting point presets |

---

## Adaptive Content

**What:** Content that changes based on user behavior or context.

### Types

| Type | Basis | Example |
|------|-------|---------|
| **Role-based** | User role/permissions | Admin vs. user views |
| **Behavior-based** | Past actions | "Continue where you left off" |
| **Context-based** | Current state | Location, device, time |
| **Preference-based** | Explicit settings | Language, theme |

### Implementation Guidelines

**DO:**
- Explain why content is personalized
- Allow users to dismiss/adjust
- Respect privacy expectations
- Provide value (not just surveillance)
- Fall back gracefully to defaults

**DON'T:**
- Be creepy (mentioning private data)
- Over-personalize (filter bubble)
- Personalize without value
- Remove access to non-personalized views
- Trap users in narrow recommendations

### Transparency Patterns

```
"Based on your recent projects"
"Because you viewed [X]"
"Popular in your region"
[See all] | [Hide these suggestions]
```

---

## User Preferences

**What:** Settings users explicitly configure.

### Common Preference Categories

| Category | Examples |
|----------|----------|
| **Display** | Theme, density, font size |
| **Communication** | Email frequency, notification types |
| **Privacy** | Data sharing, tracking |
| **Regional** | Language, timezone, currency |
| **Workflow** | Default views, keyboard shortcuts |

### Implementation Guidelines

**DO:**
- Group preferences logically
- Provide clear defaults
- Explain impact of settings
- Apply immediately (or show preview)
- Sync across devices

**DON'T:**
- Create endless settings pages
- Hide important preferences
- Require restart for simple changes
- Use jargon in preference names
- Set anti-user defaults

### Settings Page Patterns

**Grouped settings:**
```
Account
  - Profile
  - Security
  - Privacy

Preferences  
  - Appearance
  - Notifications
  - Language & Region

Integrations
  - Connected apps
  - API keys
```

**Inline settings:**
```
[Toggle] Enable email notifications
        Get notified about new messages
        
[Dropdown] Frequency: [Daily digest ▼]
```

---

## Localization (l10n)

**What:** Adapting interfaces for different languages and regions.

### Key Considerations

| Element | Localization Needs |
|---------|-------------------|
| **Text** | Translation, expansion space |
| **Dates** | Format varies by region |
| **Numbers** | Decimal/thousand separators |
| **Currency** | Symbol, position, format |
| **Direction** | LTR vs. RTL layouts |
| **Images** | Cultural appropriateness |
| **Legal** | Region-specific requirements |

### Implementation Guidelines

**DO:**
- Design for text expansion (German ~30% longer)
- Use Unicode/UTF-8 throughout
- Externalize strings (no hardcoding)
- Support RTL layouts
- Test with real translations
- Consider cultural context

**DON'T:**
- Concatenate strings for sentences
- Use flags for language selection
- Assume formats (dates, addresses)
- Hardcode text in images
- Use culturally specific idioms

### Text Expansion Guidelines

| Language | Expansion vs. English |
|----------|----------------------|
| German | +30% |
| French | +20% |
| Spanish | +20% |
| Chinese | -30% (but vertical space) |
| Japanese | -20% |
| Arabic | +25% (RTL) |

---

## Smart Defaults

**What:** Pre-selecting the most likely option.

### Default Sources

| Source | Example |
|--------|---------|
| **User history** | Last used option |
| **User profile** | Location-based defaults |
| **Behavior patterns** | Most common choice |
| **Context** | Time-appropriate defaults |
| **System intelligence** | ML-predicted preference |

### Implementation Guidelines

**DO:**
- Save and reuse user preferences
- Use sensible fallbacks
- Make overriding easy
- Be transparent about defaults
- Respect explicit user choices

**DON'T:**
- Force users into defaults
- Reset preferences unexpectedly
- Use defaults against user interest
- Make changing defaults hard
- Assume all users are the same

### Examples

```
New document: Default to last-used template
Date picker: Default to today
Country: Default to detected location
Currency: Default to account currency
Recipient: Default to recent contacts
```

---

## Recommendation Systems

**What:** Suggesting content based on user data.

### Types

| Type | Basis | Example |
|------|-------|---------|
| **Collaborative** | Similar users' behavior | "Users like you also bought" |
| **Content-based** | Item similarity | "Similar to items you viewed" |
| **Hybrid** | Combined approaches | "Recommended for you" |

### Implementation Guidelines

**DO:**
- Explain recommendation basis
- Allow feedback (helpful/not helpful)
- Include diversity (avoid filter bubble)
- Update recommendations regularly
- Provide "see more like this" options

**DON'T:**
- Show only narrow recommendations
- Recommend items already purchased/viewed
- Use recommendations for upselling only
- Hide non-recommended options
- Persist stale recommendations

### Recommendation UI Patterns

```
"Because you watched [X]"
[Thumbnail] [Thumbnail] [Thumbnail]
            [See all →]

"Popular with marketers"
[Item] [Item] [Item]
[Not interested]
```

---

## Progressive Profiles

**What:** Building user profiles over time rather than all at once.

### Benefits

- **Reduced friction** — Don't ask everything upfront
- **Better data** — Ask in context when relevant
- **Ongoing relationship** — Learn more over time

### Implementation Guidelines

**DO:**
- Ask for minimum to start
- Request additional info contextually
- Explain why you're asking
- Make additions optional
- Show value of providing info

**DON'T:**
- Front-load all questions
- Ask for irrelevant information
- Require full profiles to start
- Nag for profile completion
- Ask repeatedly for declined info

### Contextual Profile Building

```
[First use] → Email only
[First project] → "What type of project is this?" (improves suggestions)
[Two weeks in] → "Add profile photo for team collaboration"
[First export] → "What file formats do you prefer?" (remembers choice)
```

---

## Personalization Audit

| Element | Implemented? | Value to User? |
|---------|--------------|----------------|
| ☐ Customizable dashboard | | |
| ☐ Saved preferences | | |
| ☐ Smart defaults | | |
| ☐ Content recommendations | | |
| ☐ Regional localization | | |
| ☐ Progressive profiling | | |
| ☐ User-controlled options | | |
| ☐ Transparency about personalization | | |
