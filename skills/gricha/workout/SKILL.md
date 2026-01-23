---
name: workout
description: Track workouts, log sets, manage exercises and templates with workout-cli. Use when helping users record gym sessions, view history, or analyze strength progression.
metadata: {"clawdbot":{"emoji":"🏋️"}}
---

# Workout CLI

CLI for tracking workouts, managing exercises, and analyzing training progress.

## Installation

```bash
git clone https://github.com/gricha/workout-cli.git
cd workout-cli
bun install
bun run build
# Binary at ./dist/workout
```

Requires: [Bun](https://bun.sh) >= 1.3.5

## Quick Reference

| Action | Command |
|--------|---------|
| Start workout | `workout start --empty` or `workout start <template>` |
| Log sets | `workout log bench-press 135 8,8,7,6` |
| Add note | `workout note "Felt strong"` |
| Swap exercise | `workout swap bench-press dumbbell-bench-press` |
| Finish | `workout done` |
| View last | `workout last` |
| Check PRs | `workout pr` |

---

## Workout Sessions

### Start a Workout

```bash
# Freestyle session (most common)
workout start --empty

# From template
workout start push-day

# Resume interrupted
workout start --continue
```

### Log Sets

```bash
# Multiple sets at same weight
workout log bench-press 135 8,8,7,6

# Progressive weights (call multiple times)
workout log squat 135 10
workout log squat 185 8
workout log squat 225 5,5,5

# Relative to last session
workout log deadlift +10 5

# With RIR tracking
workout log bench-press 185 8 --rir 2
```

### Notes

```bash
# Session-level note
workout note "Elbow felt tight on pulling movements"

# Exercise-specific note
workout note lat-pulldown "Dropped weight due to elbow"
```

### Swap & Add

```bash
# Swap an exercise (moves logged sets to new exercise)
workout swap bench-press dumbbell-bench-press

# Add exercise mid-workout
workout add face-pulls
```

### Finish or Cancel

```bash
# Complete and save
workout done
# Shows: duration, total sets, volume, muscles worked

# Discard without saving
workout cancel
```

### Check Status

```bash
workout status
# Shows current exercises, sets logged, and notes
```

---

## Exercise Library

### List Exercises

```bash
workout exercises list
workout exercises list --muscle chest
workout exercises list --type compound
```

### Add Custom Exercise

⚠️ **All three options required:**

```bash
workout exercises add "Bayesian Cable Curl" \
  --muscles biceps \
  --type isolation \
  --equipment cable

workout exercises add "Single Arm Cable Row" \
  --muscles back,lats \
  --type compound \
  --equipment cable
```

### Show/Edit/Delete

```bash
workout exercises show bench-press
workout exercises edit bench-press --notes "Pause at bottom"
workout exercises delete my-custom-exercise
```

---

## Templates

```bash
# List templates
workout templates list

# Create template
workout templates create "Push Day" \
  -e "bench-press:4x8-12, overhead-press:3x8-10, lateral-raise:3x12-15"

# Show template
workout templates show push-day

# Delete template
workout templates delete push-day
```

---

## History & Analytics

### Last Workout

```bash
workout last
workout last --full
```

### Exercise History

```bash
workout history bench-press
workout history squat --last 20
```

### Personal Records

```bash
workout pr
workout pr bench-press
workout pr --muscle chest
```

Shows weight × reps with estimated 1RM.

### Volume Analysis

```bash
workout volume              # Last 4 weeks
workout volume --week
workout volume --month
workout volume --by muscle
workout volume --by exercise
```

### Progression

```bash
workout progression bench-press
# Shows: date, best set, estimated 1RM, volume over time
```

---

## Typical Session

```bash
# 1. Start
workout start --empty

# 2. Log as you go
workout log lat-pulldown 100 10,10,9,8
workout note lat-pulldown "Dropped from 120 due to elbow"
workout log single-arm-cable-row 40 12,12,10
workout log single-arm-cable-row 45 10,10
workout log reverse-pec-deck 75 15,15
workout log reverse-pec-deck 80 12,12

# 3. Add session notes
workout note "Pull day - elbow still recovering"

# 4. Finish
workout done
```

---

## Data Storage

```
~/.workout/
  exercises.json   # Exercise library
  workouts/        # Completed sessions
```

## JSON Output

All commands support `--json`:

```bash
workout pr --json
workout last --json
workout history squat --json
```

## Gotchas

- **exercises add** requires all three: `--muscles`, `--type`, `--equipment`
- Weights are in **lbs** by default
- Multiple calls to `log` at different weights work fine (common pattern)
- `swap` moves all logged sets to the new exercise
- `note <exercise> <text>` adds note to specific exercise; `note <text>` adds session note

## References

- Repository: https://github.com/gricha/workout-cli
