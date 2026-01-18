# Checklist: Improving Fidelity

Systematic checks for completing interface designs beyond the happy path.

---

## Component States

Every interactive component needs these states defined:

### Core States

☐ **Default** — Resting state, no interaction
☐ **Hover** — Cursor over element (desktop)
☐ **Active/Pressed** — During click/tap
☐ **Focus** — Keyboard navigation highlight
☐ **Disabled** — Not currently interactive
☐ **Loading** — Processing/fetching
☐ **Error** — Invalid state
☐ **Success** — Action completed

### Additional States by Component Type

**Buttons:**
☐ Primary, secondary, tertiary variants
☐ Icon-only versions
☐ With/without icons
☐ Size variants (small, medium, large)

**Inputs:**
☐ Empty, filled, placeholder
☐ Valid, invalid, warning
☐ With helper text, error message
☐ Required indicator
☐ Read-only, disabled

**Checkboxes/Radios:**
☐ Unchecked, checked, indeterminate
☐ Disabled states for each

**Toggles:**
☐ On, off, disabled
☐ With labels, without labels

**Links:**
☐ Default, visited, hover, active, focus

---

## Primary Interactions

Main actions users take with the interface.

### Click/Tap Interactions

☐ **Touch targets** — Minimum 44x44px (mobile), 32x32px (desktop)
☐ **Hit areas** — Larger than visual element when needed
☐ **Feedback** — Immediate visual response to tap
☐ **Double-click/tap** — Behavior defined or prevented

### Form Submissions

☐ **Submit button states** — Enabled only when valid
☐ **In-progress feedback** — Loading indicator
☐ **Success confirmation** — Clear completion message
☐ **Error handling** — What happens when it fails?
☐ **Re-submission** — Can users retry?

### Selection Interactions

☐ **Single selection** — Radio buttons, dropdowns
☐ **Multi-selection** — Checkboxes, multi-select
☐ **Range selection** — Shift-click behavior
☐ **Select all/none** — Bulk selection

---

## Secondary Interactions

Supporting interactions beyond primary actions.

### Hover Interactions (Desktop)

☐ **Tooltips** — Delay before showing (300-500ms)
☐ **Preview cards** — Information on hover
☐ **Menu reveals** — Dropdown on hover vs. click
☐ **State changes** — Visual feedback on hover

### Long-Press (Mobile)

☐ **Context menus** — What actions appear?
☐ **Drag initiation** — Does long-press start drag?
☐ **Haptic feedback** — Vibration on trigger?

### Keyboard Interactions

☐ **Tab order** — Logical focus sequence
☐ **Enter/Space** — Activate focused element
☐ **Escape** — Close modals, cancel actions
☐ **Arrow keys** — Navigate within components
☐ **Shortcuts** — Power user key combinations

### Gestures (Mobile/Touch)

☐ **Swipe** — Horizontal/vertical actions
☐ **Pinch/zoom** — Image viewing, maps
☐ **Pull-to-refresh** — List refresh
☐ **Drag and drop** — Reordering

---

## Content Scalability

Designs must handle variable content.

### Empty States

☐ **First-time user** — No data yet, clear CTA to start
☐ **No results** — Search/filter with no matches
☐ **Deleted content** — After removing items
☐ **Error state** — Failed to load

**Empty state must include:**
- Explanation of why empty
- What user can do (CTA)
- Visual to reduce starkness

### Minimal Content

☐ **One item in list** — Does layout still work?
☐ **Short text** — Single word titles, descriptions
☐ **Missing optional fields** — Graceful absence

### Maximum Content

☐ **Long text** — Truncation with ellipsis, tooltips
☐ **Many items** — Pagination, infinite scroll, virtualization
☐ **Long words** — Word-break behavior
☐ **Large images** — Aspect ratio handling

### Edge Cases

☐ **Special characters** — Unicode, emoji, RTL text
☐ **Numbers** — Negative, decimals, large numbers
☐ **Dates** — Different formats, timezones
☐ **Names** — Mononyms, very long names, special characters

---

## System Feedback

How the interface communicates state to users.

### Loading States

☐ **Initial load** — Skeleton screens, spinners
☐ **Action processing** — Button loading state
☐ **Background loading** — Subtle indicators
☐ **Partial loading** — Progressive content reveal

**Rules:**
- < 100ms: No indicator needed
- 100ms-1s: Simple spinner
- 1s+: Progress indicator or skeleton
- 10s+: Background processing with notification

### Success Feedback

☐ **Inline confirmation** — Check marks, color changes
☐ **Toast notifications** — Non-blocking success messages
☐ **Page transitions** — Navigate to success state
☐ **Celebrations** — Milestone achievements

### Error Feedback

☐ **Inline errors** — Field-level validation
☐ **Summary errors** — Form-level error list
☐ **System errors** — Server/network failures
☐ **Recovery guidance** — What can user do?

### Progress Indicators

☐ **Determinate** — Known duration (progress bar with %)
☐ **Indeterminate** — Unknown duration (spinner)
☐ **Steps** — Multi-step process indicator
☐ **Upload/download** — File transfer progress

---

## User Input

Handling all forms of user data entry.

### Text Input

☐ **Character limits** — Max length with counter
☐ **Input masks** — Phone, credit card, date formats
☐ **Autocomplete** — Suggestions while typing
☐ **Auto-capitalization** — Appropriate for input type
☐ **Spell check** — Enabled/disabled appropriately

### Validation

☐ **Real-time validation** — Validate as user types
☐ **On-blur validation** — Validate when leaving field
☐ **On-submit validation** — Final check before submit
☐ **Error message placement** — Below field, inline
☐ **Error message content** — Clear, actionable

### Input Types

☐ **Text** — Default, email, password, URL, search
☐ **Number** — With constraints (min, max, step)
☐ **Date/time** — Native or custom pickers
☐ **File upload** — Drag-drop, click to browse
☐ **Rich text** — Formatting toolbar

### Accessibility

☐ **Labels** — Every input has a label
☐ **Placeholders** — Not used as labels
☐ **Error announcements** — Screen reader accessible
☐ **Required fields** — Clearly indicated

---

## Navigation

Moving through the interface.

### Global Navigation

☐ **Current location** — Where am I?
☐ **Available destinations** — Where can I go?
☐ **Path taken** — How did I get here? (breadcrumbs)
☐ **Return path** — How do I go back?

### State Preservation

☐ **Browser back** — Does it work as expected?
☐ **Deep linking** — Can users share URLs to specific states?
☐ **Form state** — Is data preserved on navigation?
☐ **Scroll position** — Preserved or reset appropriately?

### Transitions

☐ **Page transitions** — Consistent animation pattern
☐ **Loading transitions** — Skeleton to content
☐ **Modal/drawer open/close** — Smooth animations
☐ **List additions/removals** — Animated changes

---

## Quick Fidelity Audit

Use this for rapid checks:

| Category | ✓ | Notes |
|----------|---|-------|
| All component states defined | | |
| Primary interactions specified | | |
| Secondary interactions specified | | |
| Empty states designed | | |
| Max content handling defined | | |
| Loading states defined | | |
| Success/error feedback defined | | |
| All inputs validated | | |
| Navigation complete | | |
| Keyboard accessible | | |
