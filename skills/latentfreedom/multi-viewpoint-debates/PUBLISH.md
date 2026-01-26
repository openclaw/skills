# Publishing to ClawdHub

## Skill Info

- **Name:** `multi-viewpoint-debates`
- **Version:** 1.0.0
- **Author:** Qubit (N)
- **Description:** Spawn isolated sub-agents with distinct worldviews (Elon, Capitalist, Monkey) to debate decisions and expose blind spots through genuine disagreement.

## Structure

```
multi-viewpoint-debates/
├── SKILL.md (required) - Main skill documentation
├── VERSION - Version number (1.0.0)
├── scripts/
│   └── run-debate.sh - Helper script to generate spawn commands
├── references/
│   ├── elon.md - Elon Musk persona definition
│   ├── capitalist.md - Capitalist persona definition
│   ├── monkey.md - Monkey persona definition
│   └── how-to-debate.md - Comprehensive guide to running debates
└── assets/
    └── debate-template.md - Template for saving debates
```

## How to Publish to ClawdHub

### Prerequisites

1. Install ClawdHub CLI if you haven't:
```bash
npm install -g clawdhub
```

2. Login to ClawdHub:
```bash
clawdhub login
clawdhub whoami
```

### Publish Command

```bash
clawdhub publish /home/nick/clawd/skills/multi-viewpoint-debates \
  --slug multi-viewpoint-debates \
  --name "Multi-Viewpoint Debates" \
  --version 1.0.0 \
  --changelog "Initial release: Spawn Elon, Capitalist, and Monkey personas to debate decisions with built-in archive system."
```

### Verify Publication

After publishing, verify it's on ClawdHub:

```bash
clawdhub search "multi-viewpoint-debates"
```

## Installation for Others

Once published, users can install with:

```bash
clawdhub install multi-viewpoint-debates
```

## Using the Skill

After installation, users can:

1. **Run the helper script:**
```bash
cd skills/multi-viewpoint-debates/scripts
./run-debate.sh "Your decision here"
```

2. **Or spawn manually in Clawdbot:**
```
I want to debate whether to continue working on Brain Dump. Use the multi-viewpoint-debates skill with Elon, Capitalist, and Monkey to give me three perspectives.
```

## Future Updates

To update the skill for future versions:

1. Update VERSION file
2. Update SKILL.md or reference materials as needed
3. Publish with new version number:

```bash
clawdhub publish /home/nick/clawd/skills/multi-viewpoint-debates \
  --slug multi-viewpoint-debates \
  --name "Multi-Viewpoint Debates" \
  --version 1.1.0 \
  --changelog "Added [feature/fix]"
```

## Feature Ideas for Future Versions

- Debate history and pattern analysis
- Custom persona creation workflow
- Integration with GitHub issues (debate PRs)
- Decision outcome tracking
- Team debate mode (multiple humans debating same topic)
- Persona customization per debate
