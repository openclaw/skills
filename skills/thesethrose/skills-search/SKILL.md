---
name: skills-search
description: Search skills.sh registry from CLI. Find and discover agent skills from the skills.sh ecosystem.
metadata:
  version: 1.0.4
  tags: ["search", "skills.sh", "cli"]
  clawdbot:
    requires:
      bins: ["node"]
    install:
      - id: "skill-install"
        kind: "skill"
        source: "clawdhub"
        slug: "skills-search"
        label: "Install skills-search skill"
---

# Skills.sh Search CLI

Search skills from skills.sh registry directly from your terminal.

## Install (Clawdbot)

```bash
clawdhub install skills-search
```

## Usage

```bash
# Search for skills by name
skills-search "postgres"
skills-search "web design"
skills-search "twitter"

# Show most popular skills
skills-search --popular
skills-search --popular --limit 10

# Search with install command
skills-search "web design" --show-install
```

## Examples

```
❯ skills-search "web design"
🔍 Searching skills.sh for "web design"...

✅ web-design-guidelines (16,922 installs)
   Source: vercel-labs/agent-skills
   Install: npx skills add vercel-labs/agent-skills

✅ frontend-design (566 installs)
   Source: anthropics/skills
   Install: npx skills add anthropics/skills
```

### Popular Skills

```
❯ skills-search --popular --limit 5
📈 Top 5 most popular skills:

✅ vercel-react-best-practices (22,475 installs)
   Source: vercel-labs/agent-skills

✅ web-design-guidelines (17,135 installs)
   Source: vercel-labs/agent-skills

✅ upgrading-expo (1,192 installs)
   Source: expo/skills
...
```

## Automation (Clawdbot)

### Step 1: Search for a skill

```bash
npx @thesethrose/skills-search "react"
```

### Step 2: Install found skill via skills CLI

After finding a skill, install it using the `skills` CLI:

```bash
npx skills add vercel-labs/agent-skills
```

**TUI Navigation Guidance:**

The `skills` CLI uses an interactive menu. Watch for prompts and navigate accordingly:

1. **Select skills** → Toggle skills you want with `space`, confirm with `enter`
2. **Select agents** → Navigate with `up`/`down`, select `Clawdbot` with `space`, confirm with `enter`
3. **Installation scope** → Choose Project (recommended) with `enter`
4. **Confirm** → Press `enter` to proceed

**Important:** The TUI may change. Pay attention to the menu options and select `Clawdbot` when prompted for agents. If unsure about any selection, ask the user for guidance.

### Step 3: Verify installation

```bash
ls ~/.clawdbot/workspace/.agents/skills/
```

## Adding Your Own Skill

Skills.sh automatically indexes GitHub repos containing `SKILL.md` files. To add your skill:

1. **Create a skill folder** with `SKILL.md` in your GitHub repo
2. **Publish to ClawdHub** for Clawdbot-specific discovery:
   ```bash
   clawdhub publish ./your-skill/ --slug your-skill --name "Your Skill" --version 1.0.0
   ```
3. **Install in Clawdbot:**
   ```bash
   clawdhub install your-skill
   ```

## Notes

- Queries https://skills.sh/api/skills (official skills.sh API)
- Results sorted by install count (most popular first)
- **Clawdbot-only**: Install via `clawdhub install skills-search`
- Skills.sh leaderboard requires GitHub repo (not needed for ClawdHub-only skills)
