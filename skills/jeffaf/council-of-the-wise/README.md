# Council of the Wise

A Clawdbot skill that spawns sub-agents to analyze ideas from multiple expert perspectives.

## What It Does

When you say "send this to the council" or "council of the wise," Clawdbot:

1. Sends a loading message: `🏛️ *The Council convenes...* (this takes 2-5 minutes)`
2. Spawns a sub-agent that analyzes your idea through multiple lenses:

- **👹 Devil's Advocate** — Challenges assumptions, finds weaknesses
- **🏗️ Architect** — High-level structure and design
- **🛠️ Engineer** — Implementation feasibility and details
- **🎨 Artist** — Voice, style, and user experience

The sub-agent returns a synthesized report with insights, concerns, and recommendations from each perspective.

## Installation

### Via ClawdHub (Coming Soon)
```bash
clawdhub install council
```

### Manual
Copy the `council/` folder to your Clawdbot skills directory:
```bash
cp -r council/ ~/clawd/skills/council/
```

## Usage

```
"Send this to the council: [your idea]"
"Council of the wise: [topic to analyze]"
"Get the council's feedback on [thing]"
```

## Example

**Input:**
> Send this to the council: I'm building a CLI tool that uses AI to help with bug bounty hunting — automated recon, AI-assisted analysis, human-in-the-loop for key decisions. Target: HackerOne programs.

**Output:**
```
## 🏛️ Council of the Wise — AI Bug Bounty Tool

### 👹 Devil's Advocate
I've seen three ways this dies:

1. **Token costs eat your bounties.** Running GPT-4 on every subdomain? 
   You'll spend $50 in tokens to find a $100 bug. Do the math first.
2. **HackerOne ToS.** "Automated scanning" is a gray area. One aggressive 
   program bans your account, you lose access to all of them.
3. **The 80% problem.** AI is great at recon. It's terrible at the creative 
   leap that finds the actual vulnerability. You'll automate the easy part 
   and still do all the hard work manually.

Path forward: Start with ONE program. Track tokens religiously. Keep human 
approval before any active testing.

### 🏗️ Architect  
The fundamental constraint is the human-AI handoff. Structure it as three layers:

1. **Recon Layer** (fully automated): subdomains, ports, tech stack
2. **Analysis Layer** (AI-assisted): "here's what looks interesting and why"
3. **Testing Layer** (human-approved): actual vulnerability validation

The AI should be a force multiplier for your attention, not a replacement. 
Design the handoff points explicitly.

### 🛠️ Engineer
Concrete build plan:

- **Week 1:** Scope parser + subfinder + httpx pipeline (no AI yet)
- **Week 2:** Add Claude for analyzing httpx output, flag interesting endpoints
- **Week 3:** Human-in-the-loop approval flow, Slack/Telegram notifications
- **Week 4:** Cost tracking dashboard, per-program budgets

Start with tools you know: Python, existing recon tools, Claude API. 
Don't build a framework — build a workflow.

### 🎨 Artist
The experience should feel like a skilled research assistant, not a robot:

- Notifications should sound human: "Found 3 interesting endpoints on 
  target.com — the /api/v2/admin looks promising, want me to dig deeper?"
- Let the user name campaigns, add notes, build a narrative
- The tool should remember context: "Last time on this program, you found..."

### ⚖️ Synthesis
**Do it, but small.** The council agrees on:
- Start with ONE HackerOne program
- Track token costs from day one
- Keep human approval for anything active
- Design for attention-multiplication, not automation

**Key decision:** Build for yourself first, or build for others? 
Recommendation: yourself first, for 3 months minimum.

**Where the council disagreed:** Engineer wants to ship fast with existing tools. 
Architect wants to design the human-AI handoff carefully first. Both valid — 
depends on whether you're exploring or committing.

---
📊 **Token Usage:** ~2.1k input / ~1.8k output tokens *(estimated)*
```

## Adding Custom Agents

Just drop a `.md` file in the `agents/` folder:

```bash
# Add a security-focused reviewer
cat > agents/Pentester.md << 'EOF'
# Pentester

*"What's the attack surface? How would I break this?"*

You think like an attacker. Every feature is a potential vulnerability...
EOF
```

The skill auto-discovers all agents — no config changes needed.

### Agent File Schema

Agent files should follow this minimal structure:

```markdown
# Agent Name

*"A memorable quote or philosophy"*

[1-2 sentences describing the perspective]

## Your Voice
[How this agent sounds — tone, example phrases]

## Your Approach
[How this agent analyzes — what they look for]
```

See the bundled agents in `agents/` for examples.

## Custom Agents

The skill includes bundled agent personas, but if you have custom PAI agents at `~/.claude/Agents/`, those will be used instead.

## HOWTO: Using Council of the Wise Effectively

### When to Use the Council
- Before committing to a major decision (new project, pivot, launch)
- When you're too close to an idea and need outside perspective
- For stress-testing plans before sharing with stakeholders
- When you're stuck and want structured thinking prompts

### When NOT to Use It
- Quick questions ("what's the syntax for X?")
- Time-sensitive tasks (takes 2-5 minutes)
- Small decisions where four perspectives is overkill
- Things you've already decided — the council isn't for validation

### Getting the Best Results

1. **Be Specific.** "Analyze my startup idea" → weak. "Analyze this B2B SaaS for security teams: [specific pitch]" → strong.

2. **Include Context.** Share constraints, goals, and what you've already considered. The council is smarter when you're honest about what you don't know.

3. **Ask Follow-ups.** After the council reports, dig into the most interesting points. "The Devil's Advocate mentioned X — expand on that."

4. **Use the Synthesis.** The individual perspectives are interesting; the synthesis is actionable. Start there if you're short on time.

### Example Invocations

```
"Send this to the council: I'm considering switching from Substack to 
Beehiiv for my newsletter. 2000 subscribers, mostly free, want to 
monetize. What should I consider?"

"Council of the wise: Review this README before I publish it — 
is the value prop clear? What's missing?"

"Get the council's feedback on this feature spec [paste spec]"
```

**Pro Tip:** Run the council *before* you're emotionally invested in an idea. It's easier to hear criticism early than after you've spent a week building.

## Why These Four Perspectives?

The council members complement each other:

- **Devil's Advocate** finds what could go wrong (risk)
- **Architect** designs how it should be structured (strategy)
- **Engineer** figures out how to build it (execution)
- **Artist** shapes how it should feel (experience)

Together they cover: risk, strategy, execution, and experience — the four dimensions most ideas need to succeed

## Credits

Inspired by [Daniel Miessler](https://danielmiessler.com/)'s PAI (Personal AI Infrastructure) concepts. The Architect, Engineer, and Artist agent personas are adapted from PAI patterns. The Devil's Advocate is an original creation.

## License

MIT
