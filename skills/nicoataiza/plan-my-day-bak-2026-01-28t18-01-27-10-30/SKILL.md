---
name: plan-my-day
description: Generate an energy-optimized, time-blocked daily plan
version: 1.0.0
author: theflohart
tags: [productivity, planning, time-blocking, energy-management]
---

# Plan My Day

Generate a clean, actionable hour-by-hour plan for the day based on current priorities and energy windows.

## Usage

```
/plan-my-day [optional: YYYY-MM-DD for future date]
```

## Planning Principles

1. **Morning Priming** - Protect your first hour for waking rituals, not tasks
2. **Energy-Based Scheduling** - Match task difficulty to energy levels
3. **Time Blocking** - Assign specific time windows to specific work
4. **Top 3 Focus** - Identify the 3 most important outcomes for the day

## Energy Windows (Customize to Your Rhythm)

- **Peak Performance:** Morning (deep work, hardest tasks)
- **Secondary Peak:** Afternoon (focused work, meetings)
- **Recovery Blocks:** Breaks for exercise, meals, rest
- **Wind Down:** Evening (lighter tasks, planning)

## Process

1. **Gather Context**
   - Check existing daily notes
   - Review current priorities
   - Identify fixed commitments (meetings, calls)
   - Check pending tasks from yesterday

2. **Identify Top 3 Priorities**
   - What MUST happen today?
   - What moves the needle most?
   - What has a deadline?

3. **Build Time-Blocked Schedule**
   - Assign priorities to peak energy windows
   - Block fixed commitments
   - Add buffer time between blocks
   - Include breaks and recovery

4. **Apply Constraints**
   - Respect existing appointments
   - Protect personal time
   - Include meal breaks
   - Don't over-schedule

## Output Format

```markdown
# Daily Plan - [Day], [Month] [Date], [Year]

## Today's Mission

**Primary Goal:** [One-sentence goal for the day]

**Top 3 Priorities:**
1. [Priority 1 with specific outcome]
2. [Priority 2 with specific outcome]
3. [Priority 3 with specific outcome]

---

## Time-Blocked Schedule

### [TIME] - [TIME]: [Block Name]
**Focus:** [Primary focus for this block]

- [ ] [Specific task 1]
- [ ] [Specific task 2]
- [ ] [Specific task 3]

**Target:** [Measurable outcome]

---

[Continue for each time block...]

---

## Success Criteria

### Must-Have (Non-Negotiable)
- [ ] [Critical task 1]
- [ ] [Critical task 2]
- [ ] [Critical task 3]

### Should-Have (Important)
- [ ] [Important task 1]
- [ ] [Important task 2]

### Nice-to-Have (Bonus)
- [ ] [Bonus task 1]

---

## Evening Check-In

- [ ] Priority 1 done? **YES / NO**
- [ ] Priority 2 done? **YES / NO**
- [ ] Priority 3 done? **YES / NO**

**What went well:**

**What got stuck:**

**Tomorrow's priority adjustment:**
```

## Decision-Making Framework

Before doing ANYTHING, ask:
1. Is this one of my top 3 priorities?
2. Does this move me toward today's goal?
3. Can this wait until tomorrow?

**If NO to all three → DON'T DO IT**

## Tips

- Don't schedule 100% of your time - leave 20% buffer
- Put your hardest task in your peak energy window
- Group similar tasks together (batching)
- Schedule breaks, don't just hope for them
- Review and adjust mid-day if needed
