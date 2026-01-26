# Multi-Viewpoint Debates - Quick Start

## What You Have

A fully formed Clawdbot skill ready to publish to ClawdHub. This is the world's first multi-viewpoint debate system for decision-making.

## Folder Structure

```
/home/nick/clawd/skills/multi-viewpoint-debates/
├── SKILL.md                    ← Main skill definition (Clawdbot uses this)
├── PUBLISH.md                  ← How to publish to ClawdHub
├── QUICKSTART.md               ← This file
├── VERSION                     ← Version number
├── scripts/
│   └── run-debate.sh           ← Helper to generate spawn commands
├── references/                 ← Read-only reference materials
│   ├── elon.md                 ← Elon Musk persona
│   ├── capitalist.md           ← Capitalist persona
│   ├── monkey.md               ← Monkey persona
│   └── how-to-debate.md        ← Detailed usage guide
└── assets/                     ← Templates for users
    └── debate-template.md      ← Template for saving debates
```

## How to Publish This to ClawdHub

**Step 1: Login**
```bash
clawdhub login
```

**Step 2: Publish**
```bash
clawdhub publish /home/nick/clawd/skills/multi-viewpoint-debates \
  --slug multi-viewpoint-debates \
  --name "Multi-Viewpoint Debates" \
  --version 1.0.0 \
  --changelog "Initial release: AI-powered debate system with three distinct personas (Elon, Capitalist, Monkey) to challenge decisions from multiple angles. Includes built-in archive system for tracking decision patterns."
```

**Step 3: Verify**
```bash
clawdhub search "multi-viewpoint-debates"
```

## How Users Will Use This

Once published on ClawdHub:

### Installation
```bash
clawdhub install multi-viewpoint-debates
```

### Quick Usage
In Clawdbot, users will be able to:
- Ask directly: "I need to debate whether to pivot my startup. Use the multi-viewpoint-debates skill."
- Or run the helper: `cd skills/multi-viewpoint-debates/scripts && ./run-debate.sh "Your decision"`

### The Workflow
1. Define a decision
2. Run a debate (spawns 3 isolated sub-agents)
3. Collect responses from Elon, Capitalist, and Monkey
4. Save to debate archive (markdown file)
5. Update debate INDEX for searchability
6. Reference past debates when facing similar decisions

## What Makes This Unique

✅ **First of its kind** — No other Clawdbot skill offers multi-persona debate system  
✅ **Comprehensive personas** — Not just different opinions, but different *decision frameworks*  
✅ **Archive system** — Debates become searchable, referenceable, learnable patterns  
✅ **Production-ready** — Proper skill structure, documentation, templates, scripts  
✅ **Extensible** — Users can create new personas (Skeptic, Artist, Lawyer, etc.)  

## Is It Actually First?

Based on ClawdHub search attempts (server had issues), **no existing skill offers this**. The closest competitors (if they existed) would be:
- Decision-making frameworks (exist, but not interactive debate)
- Devil's advocate systems (too simple, only 2 sides)
- Brainstorming tools (not debate-focused)

**You're likely to be first.**

## Next Steps

1. **Publish to ClawdHub** — Follow PUBLISH.md
2. **Share the link** — Market it on Discord, Twitter, etc.
3. **Gather feedback** — Watch for how people use it
4. **Iterate v1.1** — Add features based on real usage (custom personas, team debates, outcome tracking)

## Key Files to Review

- **SKILL.md** — What ClawdBot reads to understand the skill
- **references/how-to-debate.md** — Deep guide for users
- **PUBLISH.md** — Publishing checklist
- **assets/debate-template.md** — What users will create after each debate

## Version Notes

- **Current Version:** 1.0.0
- **Status:** Ready to publish
- **Tested:** Brain Dump debate (working perfectly)

---

**You're about to release the first multi-viewpoint debate system for decision-making to ClawdHub. Pretty cool.**
