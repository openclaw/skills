# Patterns: Error Prevention & Handling

Patterns for preventing errors and helping users recover gracefully.

---

## Core Philosophy

**Prevention > Recovery > Graceful Failure**

The best error is the one that never happens. The second best is the one users can easily fix.

---

## Error Prevention

### Constraints

**What:** Limiting input to valid options.

| Technique | Example |
|-----------|---------|
| **Input masks** | Phone: (___) ___-____ |
| **Dropdowns** | Choose from valid options |
| **Date pickers** | Can't type invalid dates |
| **Range limits** | min/max on number inputs |
| **Character limits** | maxlength on text |
| **Disabled states** | Can't click invalid options |

### Guidance

**What:** Helping users get it right the first time.

| Technique | Example |
|-----------|---------|
| **Inline hints** | "Password must be 8+ characters" |
| **Examples** | "e.g., name@example.com" |
| **Format indicators** | Showing expected format |
| **Real-time validation** | Check as user types |
| **Autocomplete** | Suggest valid values |

### Confirmations

**What:** Verifying destructive or irreversible actions.

**Use confirmation dialogs for:**
- Deleting data
- Canceling subscriptions
- Sending to many recipients
- Actions that can't be undone
- Financial transactions

**Don't overuse:** Confirmation fatigue makes users click through without reading.

---

## Form Validation

### Validation Approaches

| Approach | Pros | Cons |
|----------|------|------|
| **On blur** | Good balance, validates after field | Slight delay |
| **On submit** | Simple to implement | Errors appear late |
| **Real-time** | Immediate feedback | Can be annoying |
| **Debounced** | Good for async checks | Timing tuning needed |

### Recommended Approach

1. **Format validation** → Real-time or on blur
2. **Required fields** → On blur or on submit
3. **Async validation** → Debounced (300-500ms)
4. **Cross-field validation** → On submit

### Error Display Guidelines

**DO:**
- Show error adjacent to the field
- Use red color + icon (accessible)
- Explain the problem specifically
- Explain how to fix it
- Highlight invalid field
- Scroll to first error

**DON'T:**
- Show only at page top
- Clear user input on error
- Use only color to indicate error
- Show technical error codes
- Reset the entire form

### Error Message Template

```
[What's wrong] + [How to fix it]

Examples:
"Email must include @" → "Enter a valid email (e.g., name@example.com)"
"Password too short" → "Password must be at least 8 characters"
"Username taken" → "This username is taken. Try adding numbers or underscores."
```

---

## Undo & Redo

**What:** Allowing users to reverse their actions.

### When to Implement Undo

- Destructive actions (delete, archive, remove)
- Significant changes (formatting, reorganizing)
- Accidental actions (easy to mis-click)
- Actions without confirmation dialog

### Implementation Patterns

**Soft delete:**
- Move to trash instead of permanent delete
- Show "Undo" toast with time limit
- Allow recovery from trash

**Action undo:**
- "Undo" button in success toast
- Keyboard shortcut (Cmd/Ctrl+Z)
- Undo stack for multiple actions

**Draft preservation:**
- Auto-save drafts
- Recover unsaved work
- Version history

### Guidelines

**DO:**
- Provide undo for destructive actions
- Show clear undo affordance
- Time-limit undo window (5-30 seconds)
- Make undo discoverable
- Support keyboard shortcuts

**DON'T:**
- Require confirmation AND undo (choose one)
- Make undo window too short
- Hide undo affordance
- Forget redo after undo

---

## Error Dialogs

**What:** Communicating system errors to users.

### Error Dialog Anatomy

```
[Icon] [Error Title]

[Clear explanation of what happened]
[What the user can do about it]

[Primary Action] [Secondary Action]
```

### Error Types

| Type | Tone | Recovery Options |
|------|------|------------------|
| **User error** | Helpful, not blaming | Explain how to fix |
| **System error** | Apologetic | Retry, contact support |
| **Network error** | Informative | Retry when connected |
| **Permission error** | Clear | Request access, explain why |

### Error Message Examples

| Bad | Good |
|-----|------|
| "Error 500" | "Something went wrong on our end. Please try again." |
| "Invalid operation" | "You don't have permission to delete this. Contact an admin." |
| "Failed" | "Couldn't save your changes. Check your connection and try again." |
| "Null pointer exception" | "Something unexpected happened. Our team has been notified." |

### Guidelines

**DO:**
- Use human language
- Explain what happened
- Offer recovery action
- Log details for debugging (not shown to user)
- Apologize when it's system's fault

**DON'T:**
- Show technical details to users
- Blame the user
- Leave users stuck
- Use jargon
- Panic the user ("FATAL ERROR")

---

## Autosave & Data Recovery

**What:** Preventing data loss through automatic preservation.

### Autosave Strategies

| Strategy | Best For |
|----------|----------|
| **Continuous** | Text editors, forms (debounced) |
| **On change** | Settings, toggles |
| **On blur** | Form fields |
| **Periodic** | Long-form content (every 30-60s) |
| **Before navigation** | Forms with unsaved changes |

### Implementation Guidelines

**DO:**
- Indicate save status ("Saved", "Saving...", "Changes pending")
- Save to server when possible
- Fall back to local storage
- Recover on return
- Warn before navigating away with unsaved changes

**DON'T:**
- Save too frequently (server load)
- Save too infrequently (data loss risk)
- Fail silently
- Overwrite without user awareness
- Rely only on local storage (not synced)

### Unsaved Changes Warning

```
[Modal]
"You have unsaved changes"

If you leave, your changes will be lost.

[Leave anyway] [Stay and save]
```

---

## Graceful Degradation

**What:** Maintaining functionality when things go wrong.

### Strategies

| Failure | Graceful Response |
|---------|-------------------|
| Network down | Show cached data, queue actions |
| Feature fails | Disable feature, don't crash |
| Image fails | Show placeholder |
| Third-party down | Fallback or skip gracefully |
| Timeout | Auto-retry, then explain |

### Guidelines

**DO:**
- Anticipate failure modes
- Provide fallbacks
- Inform users of degraded state
- Maintain core functionality
- Auto-retry where appropriate

**DON'T:**
- Let one failure cascade
- Show blank screens
- Hide degraded state
- Require user action for every failure
- Give up on first error

---

## Error Prevention Checklist

| Area | Techniques Applied |
|------|-------------------|
| ☐ Input constraints (masks, limits) | |
| ☐ Guidance before errors occur | |
| ☐ Confirmation for destructive actions | |
| ☐ Appropriate validation timing | |
| ☐ Clear, actionable error messages | |
| ☐ Undo for reversible actions | |
| ☐ Autosave for data preservation | |
| ☐ Graceful handling of system errors | |
| ☐ Recovery options always available | |
