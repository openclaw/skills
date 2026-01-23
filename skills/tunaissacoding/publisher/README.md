# publisher

Make your skills easy to understand and impossible to ignore.

**The problem:** Your skills get lost in the noise because people don't understand what they do or why they matter.

**This tool:** Generates clear, compelling descriptions that make people want to download your skills, then publishes everywhere with one command.

---

## 📋 Requirements

- bash
- `jq` (`brew install jq`)
- `gh` CLI (`brew install gh`)
- `clawdhub` CLI (`npm install -g clawdhub`)
- git

---

## ⚡ What It Does

**Your skills become easy to understand and impossible to ignore.**

The tool:
- Generates compelling one-liners that explain your skill's value
- Creates clear, scannable descriptions following proven patterns
- Makes installation and setup obvious
- Publishes to GitHub and ClawdHub automatically

One command turns technical skills into must-have tools.

---

## 🚀 Installation

```bash
clawdhub install publisher
```

### First-Time Setup

**Requirements:**

```bash
# Install dependencies
brew install jq gh
npm install -g clawdhub

# Authenticate GitHub CLI
gh auth login
```

**That's it!** The tool handles the rest.

### What Happens

The installation:
- Adds the `skill-publisher` command to your PATH
- Validates all dependencies are installed
- Checks GitHub authentication

---

## 🔧 How It Works

**Result:** People understand your skill's value immediately and want to download it.

**The process:**

1. **Analyzes** your SKILL.md to extract the core value proposition
2. **Generates** 3 one-liner options using proven patterns:
   - Pattern A: Continuous benefit ("Keep X fresh 24/7")
   - Pattern B: Elimination ("Do X without Y")
   - Pattern C: Automation ("Automatically X when Y")
3. **Creates** clear descriptions that explain:
   - What problem it solves (the WHY)
   - What it does (the outcome)
   - How to install (the steps)
   - How it works (the process)
4. **Publishes** to GitHub (creates repo if needed)
5. **Publishes** to ClawdHub with version from VERSION file

**Smart workflow:**
- Detects existing GitHub repos (won't duplicate)
- Asks for approval before overwriting README
- Auto-detects version from VERSION file
- Handles git initialization if needed

**Example:**

```bash
cd ~/clawd/skills/my-skill
publisher
```

Output:
```
📝 Generating one-liner options...

A) Keep your thing updated automatically 24/7
B) Update things without manual intervention
C) Automatically sync data when changes occur

Choose one-liner (A/B/C/D): A

✅ Chosen: Keep your thing updated automatically 24/7
📄 Generating README.md...
📤 Publish to GitHub and ClawdHub? (y/n): y

🐙 Creating GitHub repository...
✅ Published successfully!

📍 GitHub: https://github.com/user/my-skill
📍 ClawdHub: https://clawdhub.com/skills/my-skill
```

---
---

# 📚 Additional Information

**Everything below is optional.** The skill works out-of-the-box for most users.

This section contains:
- One-liner generation patterns
- README structure details
- File structure requirements
- Troubleshooting

**You don't need to read this for initial use.**

---

<details>
<summary><b>One-Liner Generation Patterns</b></summary>

<br>

The tool generates 3 options using proven patterns:

### Pattern A: Continuous Benefit
```
Keep [thing] [desired state] [timeframe]
```

**Examples:**
- "Keep your Claude access token fresh 24/7"
- "Keep your backups synced automatically"
- "Keep dependencies up to date daily"

### Pattern B: Elimination
```
[Do thing] without [pain point]
```

**Examples:**
- "Build cross-device tools without hardcoding paths"
- "Deploy skills without manual git commands"
- "Test code without manual setup"

### Pattern C: Automation
```
Automatically [action] [thing] [when]
```

**Examples:**
- "Automatically refresh tokens before expiry"
- "Automatically backup workspace daily"
- "Automatically update skills on schedule"

**Validation (good one-liners have):**
- ✅ Specific (not generic)
- ✅ Benefit-focused (what it does FOR YOU)
- ✅ Outcome-oriented (the result you get)
- ✅ User-focused (not technical jargon)

</details>

<details>
<summary><b>README Structure Generated</b></summary>

<br>

Follows GitHub's documentation best practices:

### Essential Sections
- Title + subtitle
- **The problem:** (explains pain point)
- **This tool:** (how it solves it)
- ⚡ **What It Does** (value proposition first)
- 🛠️ **Getting Ready** (OS + Homebrew installs + external tools)
- 🚀 **Installation** (the skill itself + verification)
- 🔧 **How It Works** (result → process)

### Optional Sections (collapsible)
- Configuration options
- Troubleshooting
- For Developers
- For Developers

**Key features:**
- Inverted pyramid (conclusion first)
- Bold outcomes for scannability
- One idea per bullet
- Under 15% text highlighting
- Emojis for visual hierarchy

</details>

<details>
<summary><b>File Structure Required</b></summary>

<br>

Your skill directory should have:

```
your-skill/
├── SKILL.md           # Required: with frontmatter
├── VERSION            # Required: semantic version
├── scripts/           # Optional: your code
│   └── main.sh
├── README.md          # Generated by this tool
└── .gitignore         # Optional
```

**SKILL.md frontmatter:**
```yaml
---
name: your-skill
description: Brief description here
---
```

**VERSION file:**
```
1.0.0
```

</details>

<details>
<summary><b>Troubleshooting</b></summary>

<br>

### "gh: command not found"

Install and authenticate GitHub CLI:
```bash
brew install gh
gh auth login
```

### "Permission denied (publickey)"

GitHub authentication failed.

Re-run:
```bash
gh auth refresh -s repo
```

### "SKILL.md not found"

Create a SKILL.md with frontmatter:
```markdown
---
name: my-skill
description: What it does
---

# my-skill

Longer description here.
```

### "VERSION file not found"

Create a VERSION file:
```bash
echo "1.0.0" > VERSION
```

### "Repository already exists"

If the repo exists on GitHub but not locally:
```bash
gh repo clone username/skill-name
cd skill-name
skill-publisher
```

</details>

<details>
<summary><b>For Developers</b></summary>

<br>

### Architecture

**Phase 1: Analysis**
- Parses SKILL.md frontmatter (YAML)
- Extracts name, description
- Reads VERSION file

**Phase 2: One-Liner Generation**
- Applies 3 pattern formulas
- Lets user choose or write custom
- Updates SKILL.md frontmatter

**Phase 3: README Generation**
- Uses template structure
- Fills in skill-specific content
- Validates formatting (emojis, bold, structure)

**Phase 4: Publishing**
- Checks for existing GitHub repo
- Creates repo if needed (via `gh`)
- Pushes code
- Publishes to ClawdHub (via `clawdhub`)

### Future Enhancements (v1.1.0+)

- Full README generation from SKILL.md
- LLM-powered one-liner generation
- Automatic changelog generation
- Multiple platform support (npm, etc.)

</details>

---

## License

MIT
