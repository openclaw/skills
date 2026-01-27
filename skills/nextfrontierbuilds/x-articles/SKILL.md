---
name: x-articles
description: Create and publish X (Twitter) Articles with viral formatting, hook patterns, and browser automation. Handles Draft.js quirks, embed limitations, and image uploads.
version: 1.0.1
---

# X Articles Skill

Create, format, and publish long-form articles on X (Twitter) with proven viral patterns.

## Quick Reference

### Content Formatting Rules (CRITICAL)

X Articles uses Draft.js editor with specific quirks:

1. **Line breaks = paragraph breaks** - Each newline creates a new paragraph block with spacing
2. **Join sentences on ONE LINE** - All sentences in the same paragraph must be on a single line
3. **Use plain text, not markdown** - X Articles uses rich text, not markdown
4. **No em dashes (—)** - Replace with colons or rewrite sentences

**Wrong:**
```
Sentence one.
Sentence two.
Sentence three.
```

**Right:**
```
Sentence one. Sentence two. Sentence three.
```

### Embed Limitation (IMPORTANT)

**Embedded posts ALWAYS render at the END of the content block, not inline.**

Workarounds:
- Structure article to reference "see posts below"
- Accept visual flow: text → text → embeds at bottom
- Use `Insert > Posts` menu (don't paste URLs)

### Image Specs

| Type | Aspect Ratio | Recommended Size |
|------|--------------|------------------|
| Cover/Header | 5:2 | 1792x716 or similar |
| Inline images | 16:9 or 4:3 | 1792x1024 (DALL-E HD) |

## Viral Article Structure

### The Template

```
HOOK (hit insecurity or opportunity)

WHAT IT IS (1-2 paragraphs with social proof)

WHY MOST PEOPLE WON'T DO IT (address objections)

THE [X]-MINUTE GUIDE
- Step 1 (time estimate)
- Step 2 (time estimate)
- ...

YOUR FIRST [N] WINS (immediate value)
- Win 1: copy-paste example
- Win 2: copy-paste example

THE COST (value comparison)

WHAT TO DO AFTER (next steps)

THE WINDOW (urgency)

CTA (soft or hard)
```

### Hook Patterns That Work

**Insecurity/FOMO:**
```
everyone's talking about X... and you're sitting there wondering if you missed the window
```

**Big Opportunity:**
```
this is the biggest opportunity of our lifetime
```

**News Hook:**
```
X just open sourced the algo. Here's what it means for you:
```

**RIP Pattern:**
```
RIP [profession]. This AI tool will [action] in seconds.
```

**WTF Pattern:**
```
WTF!! This AI Agent [does amazing thing]. Here's how:
```

**Personal Story:**
```
When I was young, I was always drawn to people who...
```

### CTA Patterns

**Hard CTA (engagement bait):**
```
RT + follow + reply 'KEYWORD' and I'll send the cheat sheet
```

**Soft CTA:**
```
If you take this advice and build something, let me know!
```

**Simple:**
```
Feel free to leave a like and RT if this helped.
```

## Style Guide

### Damian Player Style (Tactical)
- All lowercase (deliberate)
- Urgent, tactical tone
- 1500+ words
- Heavy step-by-step detail
- Hard CTA with lead magnet

### Alex Finn Style (Motivational)
- Normal capitalization
- Warm, motivational tone
- 800-1200 words
- Mix of WHY and HOW
- Soft CTA + product links

### Dan Koe Style (Philosophical)
- Long-form essay (2000+ words)
- Personal storytelling opener
- Named frameworks ("The Pyramid Principle")
- Deep teaching, not just tactics
- Newsletter CTA

## Common Mistakes to Avoid

- Short articles under 500 words
- Facts without story/emotion
- No clear sections or headers
- No objection handling
- No immediate wins section
- No CTA
- Generic AI-sounding language
- Em dashes (—) everywhere
- Excessive emojis
- Pasting tweet URLs instead of using Insert menu

## Browser Automation (agent-browser)

### Prerequisites
- clawd browser running on CDP port 18800
- Logged into X on the browser

### Navigate to Article Editor
```bash
# Open new article
agent-browser --cdp 18800 navigate "https://x.com/compose/article"

# Take snapshot to see current state
agent-browser --cdp 18800 snapshot
```

### Paste Content
```bash
# Put content in clipboard
cat article.txt | pbcopy

# Click content area, select all, paste
agent-browser --cdp 18800 click '[contenteditable="true"]'
agent-browser --cdp 18800 press "Meta+a"
agent-browser --cdp 18800 press "Meta+v"
```

### Upload Cover Image
```bash
# Upload to file input
agent-browser --cdp 18800 upload 'input[type="file"]' /path/to/cover.png

# Wait for Edit media dialog, click Apply
agent-browser --cdp 18800 snapshot | grep -i apply
agent-browser --cdp 18800 click @e5  # Apply button ref
```

### Publish
```bash
# Find and click Publish button
agent-browser --cdp 18800 snapshot | grep -i publish
agent-browser --cdp 18800 click @e35  # Publish button ref

# Confirm in dialog
agent-browser --cdp 18800 click @e5   # Confirm
```

### Cleanup (Important!)
```bash
# Close tab after publishing
agent-browser --cdp 18800 tab list
agent-browser --cdp 18800 tab close 1
```

### Troubleshooting: Stale Element Refs

If clicks fail due to stale refs, use JS evaluate:
```bash
agent-browser --cdp 18800 evaluate "(function() { 
  const btns = document.querySelectorAll('button'); 
  for (let btn of btns) { 
    if (btn.innerText.includes('Publish')) { 
      btn.click(); 
      return 'clicked'; 
    } 
  } 
  return 'not found'; 
})()"
```

## Content Preparation Script

### Convert Markdown to X-Friendly Format

```bash
# scripts/format-for-x.sh
#!/bin/bash
# Converts markdown to X Articles format

INPUT="$1"
OUTPUT="${2:-${INPUT%.md}-x-ready.txt}"

cat "$INPUT" | \
  # Remove markdown headers, keep text
  sed 's/^## /\n/g' | \
  sed 's/^### /\n/g' | \
  sed 's/^# /\n/g' | \
  # Remove markdown bold/italic
  sed 's/\*\*//g' | \
  sed 's/\*//g' | \
  # Remove em dashes
  sed 's/ — /: /g' | \
  sed 's/—/:/g' | \
  # Join lines within paragraphs (keeps blank lines as separators)
  awk 'BEGIN{RS=""; FS="\n"; ORS="\n\n"} {gsub(/\n/, " "); print}' \
  > "$OUTPUT"

echo "Created: $OUTPUT"
```

## Pre-Publish Checklist

- [ ] Hook grabs attention in first line
- [ ] Objections addressed early
- [ ] Step-by-step with time estimates
- [ ] Immediate wins section included
- [ ] CTA at the end
- [ ] No em dashes (—)
- [ ] Sentences joined on single lines
- [ ] Cover image 5:2 aspect ratio
- [ ] Embeds referenced as "see below"
- [ ] Proofread for AI-sounding language

## Tweetable Quote Patterns

For promoting your article:

**Result + Cost:**
```
I gave an AI agent full access to my MacBook. It checks email, manages calendar, pushes code. Costs $20/month. A VA costs $2000.
```

**You Don't Need X:**
```
You don't need a Mac Mini. You don't need a server. I'm running my AI agent on an old MacBook Air from a drawer.
```

**Gap Warning:**
```
The gap between 'has AI agent' and 'doesn't' is about to get massive. I set mine up in 15 minutes.
```

**Urgency:**
```
Most people will bookmark this and never set it up. Don't be most people. The window is closing.
```

## Example Workflow

1. **Write article** in markdown with clear sections
2. **Run format script** to convert to X-friendly plain text
3. **Generate cover image** with DALL-E (1792x716 or 5:2 ratio)
4. **Open X article editor** via browser automation
5. **Paste content** and add section headers manually in editor
6. **Upload cover image** via file input
7. **Add inline images** at section breaks
8. **Insert embeds** (they'll appear at bottom)
9. **Preview and proofread**
10. **Publish**
11. **Post promotional tweet** with hook + article link

## Related Skills

- `bird` - X/Twitter CLI for posting tweets
- `de-ai-ify` - Remove AI jargon from text
- `ai-pdf-builder` - Generate PDFs (for lead magnets)
