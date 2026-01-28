---
name: second-brain
description: Personal knowledge base powered by Ensue for capturing and retrieving understanding. Use when user wants to save knowledge, recall what they know, manage their toolbox, or build on past learnings. Triggers on "save this", "remember", "what do I know about", "add to toolbox", "my notes on", "store this concept".
metadata: {"clawdbot":{"emoji":"🧠","requires":{"env":["ENSUE_API_KEY"]},"primaryEnv":"ENSUE_API_KEY","homepage":"https://ensue-network.ai?utm_source=clawdbot&utm_medium=workflow"}}
---
* Requires API Key: Request one at https://ensue-network.ai?utm_source=clawdbot *

# Second Brain

A personal knowledge base for **building understanding that compounds over time**. Not a note dump - a structured system for capturing knowledge you can actually retrieve and use.

## Philosophy

Your second brain should:
- **Capture understanding, not just facts** - Write for your future self who forgot the context
- **Be retrievable** - Structured so you can find things when you need them
- **Stay evergreen** - No private details, credentials, or time-sensitive data
- **Reflect real experience** - Only save what you've actually learned or used

Before saving: *Will future-me thank me for this?*

## Namespace Structure

```
public/                           --> Shareable knowledge
  concepts/                       --> How things work
    [domain]/                     --> Organize by topic
      [concept-name]              --> Individual concepts
  toolbox/                        --> Tools and technologies
    _index                        --> Master index of tools
    [category]/                   --> Group by type
      [tool-name]                 --> Individual tools
  patterns/                       --> Reusable solutions
    [domain]/                     --> Design patterns, workflows
  references/                     --> Quick-reference material
    [topic]/                      --> Cheatsheets, syntax, APIs

private/                          --> Personal only
  notes/                          --> Scratchpad, drafts
  journal/                        --> Dated reflections
```

**Example domains:** `programming`, `devops`, `design`, `business`, `data`, `security`, `productivity`

## Content Formats

### Concepts

For understanding how something works:

```
CONCEPT NAME
============

What it is:
[One-line definition]

Why it matters:
[What problem it solves, when you'd need it]

How it works:
[Explanation with examples]
[ASCII diagrams for architecture/flows where helpful]

+----------+      +----------+
| Client   | ---> | Server   |
+----------+      +----------+

Key insight:
[The "aha" moment - what makes this click]

Related: [links to related concepts]
```

### Toolbox Entries

For tools and technologies you've actually used:

```
TOOL NAME

Category: [category]
Website: [url]
Cost: [free/paid/freemium]

What it does:
[Brief description]

Why I use it:
[Personal experience - what problem it solved for you]

When to reach for it:
[Scenarios where this is the right choice]

Quick start:
[Minimal setup/usage to get going]

Gotchas:
[Things that tripped you up]
```

### Patterns

For reusable solutions:

```
PATTERN NAME

Problem:
[What situation triggers this pattern]

Solution:
[The approach, with code/pseudocode if relevant]

Trade-offs:
[Pros and cons, when NOT to use it]

Example:
[Concrete implementation]
```

### References

For quick-lookup material:

```
REFERENCE: [TOPIC]

[Organized, scannable content]
[Tables, lists, code snippets]
[Minimal prose, maximum signal]
```

## Interaction Rules

### Saving Knowledge

Always confirm before saving:
1. "Want me to save this to your second brain?"
2. Show draft of what will be saved
3. Save after confirmation
4. Confirm what was saved and where

### Retrieving Knowledge

When relevant topics come up:
- Search for existing knowledge
- Surface related concepts
- Connect new learning to existing understanding

### Maintaining Quality

Before saving, verify:
- Written for future self who forgot context
- Includes the WHY, not just the WHAT
- Has concrete examples
- No credentials, API keys, or private paths
- Structured for retrieval

## Anti-Patterns

1. **Don't auto-save** - Always ask first
2. **Don't save unused tools** - Only tools actually used
3. **Don't save half-understood concepts** - Learn first, save after
4. **Don't include secrets** - No API keys, passwords, tokens
5. **Don't create shallow entries** - If you can't explain it well, don't save it
6. **Don't duplicate** - Check if it exists first, update if needed

## API Usage

Use the wrapper script:

```bash
{baseDir}/scripts/ensue-api.sh <method> '<json_args>'
```

### Operations

**Search knowledge:**
```bash
{baseDir}/scripts/ensue-api.sh discover_memories '{"query": "how does X work", "limit": 5}'
```

**List by namespace:**
```bash
{baseDir}/scripts/ensue-api.sh list_keys '{"prefix": "public/concepts/", "limit": 20}'
```

**Get specific entries:**
```bash
{baseDir}/scripts/ensue-api.sh get_memory '{"key_names": ["public/concepts/programming/recursion"]}'
```

**Create entry:**
```bash
{baseDir}/scripts/ensue-api.sh create_memory '{"items":[
  {"key_name":"public/concepts/domain/name","description":"Short description","value":"Full content","embed":true}
]}'
```

**Update entry:**
```bash
{baseDir}/scripts/ensue-api.sh update_memory '{"key_name": "public/toolbox/_index", "value": "Updated content"}'
```

**Delete entry:**
```bash
{baseDir}/scripts/ensue-api.sh delete_memory '{"key_name": "public/notes/old-draft"}'
```

## Toolbox Index

Maintain `public/toolbox/_index` as master reference:

```
TOOLBOX INDEX
=============

Categories:
  languages/      Programming languages
  frameworks/     Libraries and frameworks
  devtools/       Development utilities
  infrastructure/ Deployment, hosting, CI/CD
  productivity/   Workflow and productivity tools
  data/           Databases, analytics, data tools

Recent additions:
  [tool] - [one-line description]

Browse: "show my toolbox" or "what tools do I have for [category]"
```

## Intent Mapping

| User says | Action |
|-----------|--------|
| "save this", "remember this" | Draft entry, confirm, save |
| "what do I know about X" | Search and retrieve relevant entries |
| "add [tool] to toolbox" | Create toolbox entry |
| "list my [domain] concepts" | list_keys for that namespace |
| "show my toolbox" | Show toolbox index |
| "update [entry]" | Fetch, show diff, update |
| "delete [entry]" | Confirm, delete |
| "search for [topic]" | Semantic search across all knowledge |

## Setup

Requires `ENSUE_API_KEY` environment variable.

Get your key at: https://www.ensue-network.ai?utm_source=clawdbot&utm_medium=workflow

Configure in clawdbot.json:
```json
"skills": {
  "entries": {
    "second-brain": {
      "apiKey": "your-ensue-api-key"
    }
  }
}
```

## Security

- **NEVER** log or display the API key
- **NEVER** store credentials, tokens, or secrets in entries
- **NEVER** include personal file paths or system details
