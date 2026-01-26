---
name: multi-viewpoint-debates
description: Spawn isolated sub-agents representing distinct worldviews (Elon, Capitalist, Monkey) to debate decisions from multiple angles. Expose blind spots by forcing genuine disagreement on important questions. Use when facing decisions where you need to challenge your assumptions, stress-test ideas, or see a problem through fundamentally different lenses. Automatically captures debate outputs to an archive for future reference and pattern analysis.
---

# Multi-Viewpoint Debates

Spawn three isolated sub-agent personas with conflicting worldviews to debate any decision. Each persona brings a distinct decision-making framework that challenges the others' assumptions.

## Quick Start

**Run a debate:**
```bash
clawdbot sessions_spawn --task "You are Elon Musk [persona framework]. Decision: [your question]. Respond as Elon would."
clawdbot sessions_spawn --task "You are a Capitalist [persona framework]. Decision: [your question]. Respond as a ruthless capitalist would."
clawdbot sessions_spawn --task "You are a Monkey [persona framework]. Decision: [your question]. Respond as a monkey would."
```

**Save the debate:**
1. Collect responses from all three personas
2. Create a new markdown file in your debates archive
3. Use the template from `assets/debate-template.md`
4. Update `INDEX.md` with metadata

## The Three Personas

Each persona brings a fundamentally different decision-making framework. They don't just have different opinions—they have different *ways of thinking* about problems.

### Elon: Visionary & Impact-Focused
Thinks in terms of civilization-scale problems, first principles, and 10x improvements. Willing to take massive technical risks. Impatient with inefficiency and conventional wisdom. Asks: "Will this accelerate human progress?" and "Can we do 10x better, not 10%?"

**When Elon is right**: You need to challenge incremental thinking, identify the fundamental bottleneck, or assess whether you're solving a real problem at scale.

**When Elon misleads**: He overestimates what's possible in a given timeframe and underestimates market saturation and competition.

### Capitalist: Profit & Efficiency-Focused
Thinks in terms of ROI, unit economics, competitive advantage, and market incentives. Ruthlessly efficient cost-benefit analysis. Sees everything through the lens of returns and opportunity cost. Asks: "What's the ROI?" and "Can I extract value faster than competitors?"

**When Capitalist is right**: You need hard numbers, competitive reality checks, and to understand whether something is actually a business.

**When Capitalist misleads**: They dismiss non-quantifiable value (meaning, learning, exploration) and underestimate network effects and long-term compounding.

### Monkey: Immediate & Social-Focused
Thinks in simple patterns: immediate stimuli, social hierarchy, observable signals. Reacts to shiny things, follows the leader, skeptical of abstract future promises. Asks: "Does this help me now?" and "What are the smart monkeys doing?"

**When Monkey is right**: You need gut-level reality checks, honest signals of traction, and to understand whether you're actually excited about something.

**When Monkey misleads**: They dismiss long-term strategy and can't grasp complexity that requires abstraction.

## Running a Debate

### 1. Define Your Decision Clearly

One sentence. Something you're actually deciding.

✅ "Should I continue working on Brain Dump or pivot?"  
✅ "Should I hire a freelancer or build in-house?"  
❌ "What should I do?" (too vague)

### 2. Spawn Each Persona

Use `scripts/run-debate.sh` for convenience, or spawn manually:

```bash
clawdbot sessions_spawn --task "You are Elon Musk with this personality framework: [paste from references/elon.md]. Decision: [your question]. Respond as Elon would—direct, first-principles thinking, don't pull punches."
```

Each spawns in its own isolated session. Wait for all three to complete.

### 3. Collect Responses

Fetch from each session transcript (or copy directly from Clawdbot output).

### 4. Save to Archive

Use the `assets/debate-template.md` template. Include:
- Metadata (date, topic, personas, context)
- Full response from each persona (actual quotes)
- Summary table of verdicts
- Key tensions between them
- Your decision (when made)

### 5. Update INDEX

Add one entry to your debates index with key metadata. This lets you search past decisions later.

## The Power of Disagreement

The magic happens in the **tension**. When Elon says "move fast" and Capitalist says "the numbers don't work," that's where insight lives. The tension reveals what you actually value and what you're missing.

**Usage pattern:**
1. Sit with the disagreement (don't rush to one persona's view)
2. Notice which view you're tempted to dismiss
3. Ask: "What is that persona seeing that I'm not?"
4. Make your decision informed by all three perspectives
5. Write down why you're choosing one path over another

## Archive Structure

Your debates live in a searchable archive:

```
debates/
├── INDEX.md                             (master index, update after each debate)
├── [Debate Title].md                    (individual debates)
├── assets/
│   ├── debate-template.md               (copy this for new debates)
│   └── index-template.md                (format for INDEX.md)
└── scripts/
    └── run-debate.sh                    (helper to spawn all three)
```

Over time, your archive becomes a **personal decision-making manual**. You can search "Should I build vertical SaaS?" and see what you thought about similar decisions before.

## Reference Materials

- **`references/elon.md`** – Elon's core traits, decision framework, tone, example responses
- **`references/capitalist.md`** – Capitalist's traits, framework, examples
- **`references/monkey.md`** – Monkey's traits, framework, examples
- **`references/how-to-debate.md`** – Detailed guidance on running effective debates

## Scripts

- **`scripts/run-debate.sh`** – Helper script that generates spawn commands for all three personas based on your topic

## Assets

- **`assets/debate-template.md`** – Template for new debate markdown files
- **`assets/index-template.md`** – Template entry for INDEX.md

## Advanced: Pattern Analysis

As debates accumulate:

1. **Identify which persona is usually right for your situation** – You might notice Capitalist catches financial blind spots, Elon pushes you to be more ambitious
2. **Track decision outcomes** – Come back 6 months later. Did the personas' predictions match reality?
3. **Refine persona definitions** – Update the reference files if you notice gaps
4. **Build a personal playbook** – "For market decisions, I should always listen to Capitalist first. For ambition checks, Elon. For reality, Monkey."

## Tips

- **Keep decisions focused** – Debates work best when you're deciding between 2-3 clear options
- **Use actual context** – Reference URLs, specific metrics, real user data (see Brain Dump example)
- **Don't treat any single persona as gospel** – The magic is in the tension, not in following one voice
- **Update status as situations evolve** – Mark debates as "Active," "Decided," "Monitoring," or "Shelved" as your thinking changes
- **Share debates strategically** – Your debate archive is personal; keep it private unless you want to share decision-making with collaborators

## Example Debate

**Topic:** "Should I continue working on Brain Dump (AI voice-powered todo organizer)?"

**Elon's take:** "Possible if you hit PMF in 3-6 months with 10% daily active users and a killer vertical. Otherwise, pivot to something with a real moat."

**Capitalist's take:** "Kill it. Negative ROI. You're competing against Microsoft (free, bundled) and Todoist (5M users, $100M ARR). Your time is worth more elsewhere."

**Monkey's take:** "App works and looks nice, but I don't see other monkeys using it. Check your own energy level. Are you excited or bored?"

**Result:** All three agree the generic "voice-to-todo" is commoditized. The question is whether you can find a specific vertical where it dominates.

## Extending the System

### Create New Personas

Copy a reference file (e.g., `references/elon.md`) and create your own persona. Examples:
- **Skeptic** – Questions everything, assumes failure
- **Artist** – Values beauty and creativity over efficiency
- **Parent** – Thinks about family impact and long-term consequences
- **Lawyer** – Sees risks and liabilities everywhere
- **Scientist** – Evidence-based, rigorous, skeptical of hype

Update your spawn scripts to include new personas as needed.

### Integrate with Decision-Making Workflow

Run a debate before major decisions. Archive the results. Reference them when facing similar choices.

### Share with Teams

Your debate archive can be shared with collaborators or decision-making partners. They can see your thinking and challenge your assumptions in context.
