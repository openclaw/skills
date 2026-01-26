# How to Run Effective Debates

## Before You Debate

### Clarify Your Decision

**What you're actually deciding:**
- 2-3 clear options (or 1 clear decision with pros/cons)
- Real stakes (this actually matters)
- Genuine uncertainty (you don't already know the answer)

**Bad debate prompts:**
- "What should I have for lunch?" (too trivial, no real stakes)
- "What should I do with my life?" (too vague, can't be debated)
- "Is my idea good?" (too open-ended, needs specificity)

**Good debate prompts:**
- "Should I leave my job to start a company or stay and invest my salary?"
- "Should I pivot Brain Dump to a specific vertical or shut it down?"
- "Should I hire a team or stay solo as long as possible?"

### Provide Context If Helpful

For decisions involving real products/projects, include:
- URL or description of what you're building
- Current metrics (users, revenue, growth)
- Market/competitive landscape
- Your constraints (time, money, energy)

**Example:** "Brain Dump is an AI voice-to-todo app at braindump.imnotbot.com. ~10 users, no revenue, solo dev, built over 3 months."

Personas use context to make specific, informed arguments rather than generic ones.

## Running the Debate

### Spawn Process

1. **Spawn Elon** — Let run to completion
2. **Spawn Capitalist** — Let run to completion
3. **Spawn Monkey** — Let run to completion

Each sub-agent runs in isolation. No interaction between them. You get three independent perspectives that don't influence each other.

### Timing

- Each persona usually takes 30-60 seconds to respond
- Wait for all three to complete before reviewing
- If one seems stuck, you can manually move on

### Collecting Responses

Copy full responses from Clawdbot output or fetch from session transcripts:
```
~/.clawdbot/agents/main/sessions/[session-id].jsonl
```

## After the Debate

### Save to Archive

Use the debate template (`assets/debate-template.md`). Include:

1. **Metadata** — Date, topic, context, your key question
2. **Full responses** — Copy exact quotes from each persona
3. **Verdicts** — 1-line summary of each persona's stance
4. **Tensions** — What do they disagree about? Where's the real conflict?
5. **Your decision** — What you're actually choosing and why
6. **Success metrics** — How will you know if you chose right?

### Update Your Index

Add one entry per debate. Examples:

```markdown
### Should I Continue Working on Brain Dump?
**File:** `Should I Continue Working on Brain Dump.md`
**Date:** 2026-01-26
**Topic:** Continue developing or pivot
**Context:** braindump.imnotbot.com - AI voice-to-todo app
**Key Question:** Is there real traction, PMF, or a killer vertical?
**Elon:** Possible if PMF in 3-6 months + 10% DAU + niche domination
**Capitalist:** Kill it. Negative ROI.
**Monkey:** Depends on your energy + real user signals
**Decision Made:** Pending
**Status:** Active review
```

## Interpreting Results

### All Three Agree

**Example:** All agree that a generic voice-to-todo is commoditized.

**Meaning:** You've found a real constraint or market reality that's hard to argue with.

**Action:** Don't ignore this. If all three perspectives agree, listen. They see something real.

### Two Agree, One Disagrees

**Example:** Elon and Monkey say "go," Capitalist says "kill it."

**Meaning:** There's a real tradeoff. Capitalist sees financial risk; others see opportunity/excitement.

**Action:** Understand the disagreement deeply. Usually:
- Capitalist is right about "this isn't a business yet"
- Elon/Monkey are right that "this might be worth doing anyway for learning/growth"

Choose consciously based on your actual priorities.

### All Disagree

**Example:** Elon says "conditional yes," Capitalist says "no," Monkey says "depends."

**Meaning:** Genuine complexity. No clear answer. Legitimate uncertainty.

**Action:** Recognize you're in real tradeoff territory. Make your decision based on YOUR values, not anyone's opinion. The debate helped you see all sides; now you choose.

## Reading the Tension

The **magic** isn't in following one persona. It's in the **tension between them**.

When Elon says "move fast, first-mover advantage" and Capitalist says "market is saturated, no moat," that's where insight lives. The tension reveals what matters:

- If you follow Elon, you're betting on speed and impact over certainty
- If you follow Capitalist, you're betting on financial viability over upside
- If you follow Monkey, you're betting on real signals and excitement over theory

**All three are valid. Choose consciously.**

## Pattern Recognition Over Time

As you accumulate debates, notice:

1. **Which persona is usually right for YOUR decisions?**
   - Capitalist catches financial blindspots
   - Elon pushes toward ambition
   - Monkey tells the truth about traction

2. **When do you ignore a persona's advice and regret it?**
   - Track this. Learn your blindspots.

3. **Do outcomes match their predictions?**
   - Come back 6 months later. Did things go as they said?
   - Update the debate file with what actually happened

4. **Build a personal playbook:**
   - "For business decisions, listen to Capitalist first"
   - "For ambition decisions, listen to Elon"
   - "For traction signals, listen to Monkey"

## Common Mistakes

❌ **Treating one persona as gospel** — They're not. They're lenses.

✅ **Use them to challenge yourself** — Which one am I tempted to dismiss? That's where my blind spot is.

---

❌ **Vague prompts** — "What should I do?" leads to vague answers.

✅ **Specific decisions** — "Should I pivot to vertical SaaS or continue as-is?" leads to focused debate.

---

❌ **Not providing context** — "Is my app good?" with no info about users, metrics, market.

✅ **Real context** — "10 daily active users, no revenue, Todoist/Notion as competitors, 3 months of development."

---

❌ **Making decisions before the debate** — Then just seeking validation.

✅ **Genuine uncertainty** — Run the debate when you don't know what to do.

---

❌ **Ignoring tension between personas** — That's where the insight lives.

✅ **Sit with disagreement** — Ask "What is that persona seeing that I'm not?"

## Integrating with Real Decisions

**Workflow:**

1. Face a real decision (ambiguous, high stakes, genuine uncertainty)
2. Define it clearly in one sentence
3. Run a debate
4. Save to archive
5. Make your decision (informed by all three perspectives)
6. Decide consciously why you're following one persona over another
7. Record success metrics
8. 6 months later: check if you were right
9. Update the debate file with outcomes

Over time, your debate archive becomes a **personal decision-making manual** showing how you think about different types of problems.

## Extending the System

**Create new personas** by copying a reference file and defining:
- Core traits
- Decision-making framework
- Tone
- Blindspots
- When to trust them

Examples: Skeptic, Artist, Parent, Lawyer, Scientist, Pessimist, Optimist

**Run multi-persona debates** with 4+ perspectives for complex decisions.

**Share debates with collaborators** so they see your thinking and can challenge specific points.

**Use debates to test strategies** before implementing them (write a strategy, debate it, then execute based on insights).
