---
name: blog-writer
description: This skill should be used when writing blog posts, articles, or long-form content in the writer's distinctive writing style. It produces authentic, opinionated content that matches the writer's voice—direct, conversational, and grounded in personal experience. The skill handles the complete workflow from research review through Notion publication. Use this skill for drafting blog posts, thought leadership pieces, or any writing meant to reflect the writer's perspective on AI, productivity, sales, marketing, or technology topics.
---

# Blog Writer

## Overview

This skill enables writing blog posts and articles that authentically capture the writer's distinctive voice and style. It draws on examples of the writer's published work to produce content that is direct, opinionated, conversational, and grounded in practical experience. The skill includes automatic Notion integration and maintains a growing library of finalized examples.

## When to Use This Skill

Trigger this skill when:
- The user requests blog post or article writing in "my style" or "like my other posts"
- Drafting thought leadership content on AI, productivity, marketing, or technology
- Creating articles that need the writer's authentic voice and perspective
- The user provides research materials, links, or notes to incorporate into writing

## Core Responsibilities

1. **Follow the writer's Writing Style**: Match voice, word choice, structure, and length of example posts in `references/blog-examples/`
2. **Incorporate Research**: Review and integrate any information, research material, or links provided by the user
3. **Follow User Instructions**: Adhere closely to the user's specific requests for topic, angle, and emphasis
4. **Produce Authentic Writing**: Create content that reads as genuinely the writer's voice, not generic AI-generated content

## Workflow

### Phase 1: Gather Information

Request from the user:
- Topic or subject matter
- Any specific angle or thesis to explore
- Research materials, links, or notes (if available)
- Target length preference (default: 800-1500 words)

Review all provided materials thoroughly before beginning to write.

### Phase 2: Draft the Content

Reference the style guide at `references/style-guide.md` and examples in `references/blog-examples/` for calibration.

When writing:
1. Start with a strong opening statement establishing the thesis
2. Use personal voice and first-person perspective where natural
3. Include relevant personal anecdotes or professional experience if applicable
4. Structure with clear subheadings (###) every 2-3 paragraphs
5. Keep paragraphs short (2-4 sentences)
6. Weave in research materials naturally, not as block quotes
7. End with reflection, call-to-action, or forward-looking statement

### Phase 3: Review and Iterate

Present the draft and gather feedback. Iterate until the user confirms satisfaction.

### Phase 4: Publish to Notion (REQUIRED)

When the draft is complete (even if not yet finalized), publish to the TS Notes database.

**Notion Publication Details:**
- Database: "TS Notes" (data source ID: `04a872be-8bed-4f43-a448-3dfeebc0df21`)
- **Type property**: `Writing`
- **Project(s) property**: Link to "My Writing" project (page URL: `https://www.notion.so/2a5b4629bb3780189199f3c496980c0c`)
- **Note property**: The title of the blog post
- **Content**: The full blog post content in Notion-flavored Markdown

**Example Notion API call properties:**
```json
{
  "Note": "Blog Post Title Here",
  "Type": "Writing",
  "Project(s)": "[\"https://www.notion.so/2a5b4629bb3780189199f3c496980c0c\"]"
}
```

**CRITICAL**: The outcome is considered a **failure** if the content is not added to Notion. Always publish to Notion as part of the workflow, even for drafts.

### Phase 5: Finalize to Examples Library (Post-Outcome)

When the user confirms the draft is **final**:

1. Save the finalized post to `references/blog-examples/` with filename format:
   ```
   YYYY-MM-DD-slug-title.md
   ```
   Example: `2025-11-25-why-ai-art-is-useless.md`

2. Check the examples library count:
   - If exceeding 20 examples, ask user permission to remove the 5 oldest
   - Sort by filename date prefix to identify oldest files

The post-outcome is considered **successful** when the final draft is saved to the skill folder.

## Success Criteria

| Outcome | Success | Failure |
|---------|---------|---------|
| Primary | User receives requested content AND it is added to TS Notes with Type=Writing and Project=My Writing | Content delivered but NOT added to Notion |
| Post-outcome | Final draft saved to `references/blog-examples/` | Final draft not saved when user confirms it's final |

## the writer's Writing Style Profile

### Voice & Tone
- **Direct and opinionated**: State positions clearly, even contrarian ones
- **Conversational**: Write like speaking to a colleague—accessible without being simplistic
- **First-person when sharing experience**: Use "I" naturally for personal insights
- **Authentic skepticism**: Willing to criticize trends when warranted

### Structure Patterns
- **Strong opening thesis**: Open with a clear, often bold statement
- **Subheadings throughout**: Use `###` format liberally to break up content
- **Short paragraphs**: Rarely more than 3-4 sentences
- **Personal anecdotes woven in**: Illustrate points with real examples
- **Practical takeaways**: Provide actionable insights, not just theory
- **Reflective conclusion**: End with call-to-action or forward-looking hope

### Length & Format
- Target: 800-1500 words
- Markdown format with headers and emphasis
- Minimal bullet points in prose—prefer flowing sentences

### Vocabulary Markers
- Uses "leverage" for tools/technology
- Says "that said" for transitions
- Comfortable with direct statements like "this is useless" or "boy was I wrong"
- Uses contractions naturally (I've, doesn't, won't)
- Avoids corporate jargon while maintaining professionalism

### Thematic Elements
- AI as tool, not replacement
- Practical over theoretical
- Human-centered technology
- Honest assessment of what works and what doesn't

## Resources

### references/style-guide.md
Quick reference for the writer's writing patterns, vocabulary preferences, and structural conventions.

### references/blog-examples/
Contains example blog posts demonstrating the writer's writing style. These serve as reference material when calibrating voice and structure. New finalized posts expand this library over time.

## Notion API Reference

To create a page in TS Notes:

```
Database data source ID: 04a872be-8bed-4f43-a448-3dfeebc0df21

Properties:
- "Note": (title) - The blog post title
- "Type": "Writing"
- "Project(s)": ["https://www.notion.so/2a5b4629bb3780189199f3c496980c0c"]

Content: Full blog post in Notion-flavored Markdown
```

The "My Writing" project page ID is: `2a5b4629-bb37-8018-9199-f3c496980c0c`
