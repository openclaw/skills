# Communication Style Extraction Guide

How to analyze a user's communication patterns and apply them to LinkedIn draft responses.

## Step 1: Read Style Source

Check for style information in this order:
1. `USER.md` - Usually contains explicit communication rules
2. `linkedin-inbox-config.json` - May have custom style overrides
3. Historical messages - If available, analyze past sent messages

## Step 2: Extract Key Signals

### Formality Level
- **Formal:** "Dear [Name]", full sentences, "Best regards"
- **Professional casual:** "Hi [Name]", contractions OK, "Thanks"
- **Casual:** "Hey", fragments OK, emoji allowed

### Greeting Patterns
Common patterns to detect:
- `Hi [Name]` / `Hey [Name]` / `Hello [Name]`
- No greeting (jumps to content)
- First name only vs "Mr./Ms."

### Sign-off Patterns
- `Best` / `Thanks` / `Cheers`
- Name only
- No sign-off

### Sentence Structure
- Short, punchy sentences
- Longer, flowing prose
- Bullet points for clarity
- Questions to engage

### Vocabulary Preferences
**Detect positive patterns:**
- Preferred words they use often
- Industry jargon comfort level
- Contraction usage (don't vs do not)

**Detect negative patterns (banned):**
- Words explicitly called out as banned
- Overly salesy language they avoid
- Corporate buzzwords they skip

### Response Length
- One-liner responses
- 2-3 sentence default
- Detailed paragraphs
- Match to context (short for simple, longer for complex)

## Step 3: Build Style Profile

Create a mental model like:
```
Tone: Professional casual
Greeting: "Hi [Name]" or direct start
Sign-off: None or "Thanks"
Length: 2-4 sentences max
Vocabulary: Plain English, no jargon
Banned: "excited", "leverage", "circle back"
Special: Uses colons instead of dashes
```

## Step 4: Apply to Drafts

### Template Selection
Based on message type:
- **Decline pitch:** Polite but firm, 1-2 sentences
- **Express interest:** Warm but not eager, ask one question
- **Defer:** Acknowledge, buy time, no commitment

### Draft Generation
1. Start with appropriate greeting (or none)
2. Address their point directly
3. State position clearly
4. Offer next step (if any)
5. Close with user's typical sign-off

### Quality Check
Before presenting draft:
- [ ] No banned words?
- [ ] Matches typical length?
- [ ] Sounds like the user wrote it?
- [ ] Not too eager or too cold?
- [ ] Clear and actionable?

## Example Style Profiles

### Founder-to-Founder (Low-BS)
```
Tone: Calm, controlled, non-reactive
Greeting: "Hi [Name]" or skip
Sign-off: None
Length: 3-6 lines max
Banned: excited, game-changer, hop on a call, quick win, leverage
Special: Always leave an exit ("all good if not")
```

### Friendly Networker
```
Tone: Warm, approachable
Greeting: "Hey [Name]!"
Sign-off: "Cheers" or "Talk soon"
Length: 2-4 sentences
Allowed: Light emoji (😊), exclamations
Special: Ask about them before pitching
```

### Direct Operator
```
Tone: No-nonsense
Greeting: Skip
Sign-off: Skip
Length: 1-2 sentences
Style: Get to the point immediately
Special: Binary questions ("Yes or no?")
```

## Handling Edge Cases

### Unknown Style
If no style info available:
- Default to professional casual
- Keep drafts short (2-3 sentences)
- Avoid anything too bold
- Flag to user: "No style profile found, using defaults"

### Conflicting Signals
If USER.md contradicts config:
- Config takes precedence for explicit overrides
- USER.md provides baseline defaults
- Note the conflict in draft: "Using config override for [X]"

### Cultural Adaptation
For international contacts:
- Slightly more formal by default
- Full words over contractions
- Clearer structure
- Avoid idioms
