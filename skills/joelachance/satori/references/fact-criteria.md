# Fact Extraction Criteria

Use this guide to determine what information is worth persisting to Satori.

## The Core Test

Ask: **"Would this information be useful if retrieved in a completely different conversation, potentially months from now, in a different application?"**

If yes → save it.
If no → skip it.

## SAVE: Notable Facts

### Decisions (High Priority)
- Technology choices: "Chose PostgreSQL over MongoDB for ACID compliance"
- Architecture decisions: "Using event sourcing pattern for audit trail"
- Business decisions: "Targeting SMB market before enterprise"
- Process decisions: "Weekly sprints, deployments on Thursdays"

### Identities & Names (High Priority)
- Project names: "Project codename is Phoenix"
- Company/product names: "Company is called Flamingo, product is FlamingoAI"
- People and roles: "Alex is the CTO, Maria handles design"
- Brand elements: "Tagline is 'Memory for machines'"

### Preferences (Medium Priority)
- Tool preferences: "Prefers Bun over Node.js"
- Style preferences: "Wants terse commit messages"
- Communication preferences: "Prefers async over meetings"
- Code style: "Uses single quotes, 2-space indent"

### Temporal Facts (High Priority)
- Deadlines: "MVP due March 15, 2025"
- Milestones: "Series A closed January 2025"
- Schedules: "Demo days are first Monday of each month"
- Version info: "Currently on v2.3, v3.0 planned for Q2"

### Context & Background (Medium Priority)
- What the project/company does: "Satori builds AI memory infrastructure"
- Problem being solved: "Cross-app context loss for AI tools"
- Key constraints: "Must work offline, no cloud dependency"
- Target users: "Developer tools teams at mid-size companies"

### Strategic Information (High Priority)
- Competitive positioning: "Differentiating on composable memory layers"
- Pricing strategy: "Freemium with usage-based enterprise tier"
- Go-to-market: "Developer-led growth, content marketing focus"
- Partnerships: "Integrating with Cursor, Claude Code first"

## DO NOT SAVE: Transient Information

### Work-in-Progress
- "The button color isn't quite right" (feedback, not decision)
- "Maybe we should consider React" (consideration, not decision)
- "I'm not sure about the naming" (uncertainty, not fact)

### Explanations & Teaching
- Claude explaining how recursion works
- Code examples written to illustrate concepts
- Debugging walkthroughs

### Session-Specific Context
- "Let's focus on the header component today"
- "I'm working on file X right now"
- Current error messages being debugged

### Obvious or Derivable
- "User is building a web app" (when already discussing React components)
- "User knows JavaScript" (when writing JS code together)

### Conversational
- Greetings, thanks, acknowledgments
- "That makes sense" / "Got it"
- Questions without answers yet

## Edge Cases

**Tentative decisions:** Save only when user confirms. "Let's go with Postgres" = save. "Maybe Postgres?" = don't save.

**Opinions vs decisions:** "I don't like ORMs" = save (preference). "ORMs are bad" = don't save (general opinion).

**Compound facts:** Combine related facts. Instead of saving "using Postgres" and "using TypeScript" and "using Bun" separately, batch: "Tech stack: TypeScript, Bun, PostgreSQL"

**Corrections:** When user corrects previous information, save the correction clearly: "Company name changed from Pelican to Flamingo"