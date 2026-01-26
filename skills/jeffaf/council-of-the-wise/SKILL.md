---
name: council
description: Send an idea to the Council of the Wise for multi-perspective feedback. Spawns sub-agents to analyze from multiple expert perspectives. Auto-discovers agent personas from agents/ folder.
version: 1.2.0
author: jeffaf
credits: Inspired by Daniel Miessler's PAI (Personal AI Infrastructure). Architect, Engineer, and Artist agents adapted from PAI patterns. Devil's Advocate is an original creation.
---

# Council of the Wise

When the user says "send it to the council" or "council of the wise" or similar, spawn a sub-agent to analyze the idea from multiple expert perspectives.

## Usage

```
"Send this to the council: [idea/plan/document]"
"Council of the wise: [topic]"
"Get the council's feedback on [thing]"
```

## Council Members

The skill **auto-discovers** agent personas from the `agents/` folder. Any `.md` file in that folder becomes a council member.

**Default members:**
- `DevilsAdvocate.md` — Challenges assumptions, finds weaknesses, stress-tests
- `Architect.md` — Designs systems, structure, high-level approach  
- `Engineer.md` — Implementation details, technical feasibility
- `Artist.md` — Voice, style, presentation, user experience

### Adding New Council Members

Simply add a new `.md` file to the `agents/` folder:

```bash
# Add a security reviewer
echo "# Pentester\n\nYou analyze security implications..." > agents/Pentester.md

# Add a QA perspective  
echo "# QATester\n\nYou find edge cases..." > agents/QATester.md
```

The skill will automatically include any agents it finds. No config file needed.

### Custom Agent Location (Optional)

If the user has custom PAI agents at `~/.claude/Agents/`, those can be used instead:
- Check if `~/.claude/Agents/` exists and has agent files
- If yes, prefer custom agents from that directory
- If no, use the bundled agents in this skill's `agents/` folder

## Process

1. Receive the idea/topic from the user
2. Discover available agents (scan `agents/` folder or custom path)
3. Send a loading message to the user: `🏛️ *The Council convenes...* (this takes 2-5 minutes)`
4. Spawn a sub-agent with **5-minute timeout** using this task template:

```
Analyze this idea/plan from multiple expert perspectives.

**The Idea:**
[user's idea here]

**Your Task:**
Read and apply these agent perspectives from [AGENT_PATH]:
[List all discovered agents dynamically]

For each perspective:
1. Key insights (2-3 bullets)
2. Concerns or questions  
3. Recommendations

End with:
- **Synthesis** section combining best ideas and flagging critical decisions
- Note where council members **disagree** with each other — that's where the insight is
- **Token Usage** with estimated input/output tokens (based on content length)

Use the voice and personality defined in each agent file. Don't just list points — embody the perspective.
```

5. Return the consolidated feedback to the user

## Output Format

```markdown
## 🏛️ Council of the Wise — [Topic]

### 👹 Devil's Advocate
[challenges and risks — sharp, probing voice]

### 🏗️ Architect  
[structure and design — strategic, principled voice]

### 🛠️ Engineer
[implementation notes — practical, direct voice]

### 🎨 Artist
[voice and presentation — evocative, user-focused voice]

### ⚖️ Synthesis
[combined recommendation + key decisions needed]
[note where council members disagreed and why — that's the gold]

---
📊 **Token Usage:** ~X input / ~Y output tokens *(estimated)*
```

## Configuration

No config file needed. The skill auto-discovers agents and uses sensible defaults:

- **Timeout:** 5 minutes (enforced via sub-agent spawn)
- **Agents:** All `.md` files in `agents/` folder
- **Output:** Markdown with synthesis and token usage
- **Model:** Uses session default (can override via Clawdbot)

## Notes

- Council review takes 2-5 minutes depending on complexity
- Use for: business ideas, content plans, project designs, major decisions
- Don't use for: quick questions, simple tasks, time-sensitive requests
- Token usage is estimated based on content length (not precise API measurement)
- Add specialized agents for domain-specific analysis (security, legal, etc.)
