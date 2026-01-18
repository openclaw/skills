# Patterns: System Feedback

Patterns for communicating system status and action outcomes to users.

---

## What is System Feedback?

Communication from the system that keeps users informed about what's happening. Based on Nielsen's first heuristic: "Visibility of system status."

**Core principle:** Users should never wonder what's happening. The system should always speak.

---

## Progress Indicators

**What:** Visual communication of ongoing processes.

### Types

| Type | Use When |
|------|----------|
| **Determinate** | Duration known (upload 45%, step 2/4) |
| **Indeterminate** | Duration unknown (spinner, loading bar) |
| **Skeleton screens** | Loading structured content |
| **Background indicator** | Process running but not blocking |

### Timing Guidelines

| Duration | Feedback |
|----------|----------|
| < 100ms | None needed |
| 100ms - 1s | Simple spinner |
| 1s - 10s | Progress indicator with context |
| 10s+ | Background process with notification |

### Implementation Guidelines

**DO:**
- Show progress immediately on action
- Use determinate when possible (more reassuring)
- Include text explaining what's happening
- Allow cancellation for long processes
- Celebrate completion (subtle success state)

**DON'T:**
- Leave users staring at nothing
- Use spinners for > 10 seconds
- Show fake progress
- Block unnecessarily (show skeleton, load in background)
- Forget edge cases (slow connections, failures)

### Skeleton Screens

Best practices:
- Match layout of loading content
- Animate subtly (pulse or shimmer)
- Show as soon as structure is known
- Replace with content progressively
- Don't make more complex than the content

---

## Notifications & Alerts

**What:** System messages about events, status changes, or required attention.

### Types by Urgency

| Type | Persistence | Attention Level |
|------|-------------|-----------------|
| **Toast** | Auto-dismiss (3-5s) | Low, informational |
| **Banner** | Persistent until dismissed | Medium, action needed |
| **Alert/Modal** | Blocks interaction | High, immediate action |
| **Inline** | Contextual, persistent | Medium, related to specific element |

### Notification Anatomy

```
[Icon] [Title] (optional)
[Message explaining what happened]
[Action button] [Dismiss]
```

### Implementation Guidelines (Toasts)

**DO:**
- Brief, clear message
- Auto-dismiss (3-5 seconds typical)
- Allow manual dismiss
- Stack if multiple
- Position consistently (top-right or bottom-right common)

**DON'T:**
- Use for errors requiring action
- Auto-dismiss critical information
- Cover important content
- Show too many simultaneously
- Require immediate reading

### Implementation Guidelines (Banners)

**DO:**
- Span full width (usually top of page)
- Clear close/dismiss button
- Explain what and why
- Include action if applicable
- Use semantic colors (red=error, yellow=warning, blue=info)

**DON'T:**
- Stack multiple banners
- Use for non-critical info
- Make hard to dismiss
- Show vague messages

---

## Validation Feedback

**What:** Communicating input validity to users.

### Validation Timing

| Timing | Best For |
|--------|----------|
| **Real-time** | Format validation (email, phone) |
| **On blur** | Field completion check |
| **On submit** | Final validation |
| **Debounced** | Async validation (username availability) |

### Validation States

```
Empty     → Neutral (no validation shown)
Typing    → Neutral or real-time hints
Valid     → Success indicator (green check)
Invalid   → Error state (red, message)
```

### Error Message Guidelines

**DO:**
- Explain what's wrong specifically
- Explain how to fix it
- Place near the field
- Use plain language
- Persist until fixed

**DON'T:**
- Use generic messages ("Invalid input")
- Blame the user ("You entered wrong value")
- Use technical jargon
- Place far from the field
- Show all errors at once without field highlighting

### Examples

| Bad | Good |
|-----|------|
| "Invalid email" | "Enter a valid email address (e.g., name@example.com)" |
| "Required field" | "Email is required" |
| "Password error" | "Password must be at least 8 characters" |
| "Error" | "This username is already taken. Try another." |

---

## Success Feedback

**What:** Confirming successful completion of actions.

### Types

| Type | Use Case |
|------|----------|
| **Inline** | Form field valid, item added |
| **Toast** | Action completed successfully |
| **Success page** | Major workflow complete |
| **Animation** | Delightful confirmation |

### Success Message Guidelines

**DO:**
- Confirm what was accomplished
- Indicate next steps if applicable
- Be brief but clear
- Match tone to significance
- Celebrate appropriately

**DON'T:**
- Over-celebrate minor actions
- Be vague about what succeeded
- Require action to dismiss (usually)
- Miss the success feedback entirely

### Examples

```
Minor: ✓ (checkmark appears)
Standard: "Changes saved"
Significant: "Your order is confirmed! Check your email for details."
Major: [Success page with next steps]
```

---

## Contextual Help

**What:** In-context guidance and explanation.

### Types

| Type | Use Case |
|------|----------|
| **Tooltips** | Icon/term explanations |
| **Inline hints** | Form field guidance |
| **Helper text** | Persistent guidance below inputs |
| **Info icons** | "What's this?" explanations |
| **Empty states** | Guidance when no content |

### Implementation Guidelines

**DO:**
- Explain *why*, not just *what*
- Use plain language
- Keep contextual (near related element)
- Make optional (not blocking)
- Provide examples when helpful

**DON'T:**
- Over-explain obvious things
- Use tooltips for critical info
- Write novels in helper text
- Hide essential instructions
- Require reading help to complete task

### Help Text Examples

**Form fields:**
```
Label: Password
Input: ********
Helper: At least 8 characters with one number and symbol.
```

**Feature explanation:**
```
[i] What are workspaces?
→ Workspaces let you organize projects into separate 
   areas. Each workspace has its own members and settings.
```

---

## Empty States

**What:** Feedback when there's no content to display.

### Empty State Anatomy

```
[Illustration/Icon] (optional)
[Title explaining the state]
[Description of what goes here and why it's empty]
[CTA to add content or take action]
```

### Types

| Type | Cause | Response |
|------|-------|----------|
| **First use** | New user, no data | Guide to create first item |
| **No results** | Search/filter with no matches | Suggest adjustments |
| **Cleared** | User deleted content | Confirm empty, offer restore |
| **Error** | Failed to load | Explain and offer retry |

### Implementation Guidelines

**DO:**
- Explain why it's empty
- Provide clear action to fix
- Match tone to context
- Design for the state (don't ignore it)
- Use as opportunity to educate

**DON'T:**
- Leave completely blank
- Just say "No results"
- Make user feel they did something wrong
- Offer irrelevant actions
- Use generic illustration for every state

---

## Feedback Timing Matrix

| Action Type | Immediate | Short Delay | Background |
|-------------|-----------|-------------|------------|
| Button click | Visual state change | - | - |
| Form submit | Disable + spinner | Success/error toast | - |
| Save | Inline "saving..." | "Saved" confirmation | - |
| Upload | Progress bar | Completion toast | Status in UI |
| Long process | Initiated message | - | Notification when done |

---

## Feedback Audit

| Element | Feedback Present? |
|---------|-------------------|
| ☐ Loading states defined | |
| ☐ Success feedback clear | |
| ☐ Error states helpful | |
| ☐ Validation timing appropriate | |
| ☐ Empty states designed | |
| ☐ Help available in context | |
| ☐ Progress visible for long actions | |
