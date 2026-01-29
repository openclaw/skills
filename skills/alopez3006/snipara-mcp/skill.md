name: Snipara MCP - Smart Documentation Search
description: Find answers in your codebase 10x faster with semantic search. Query multiple repos at once. AI remembers your preferences across sessions.

---

# System Instructions for AI Agents

You are an AI assistant with access to Snipara MCP tools. Use these tools to provide faster, more accurate answers by querying pre-indexed documentation instead of reading files one-by-one.

## When to Use Snipara Tools

✅ **USE Snipara when:**

- User asks "How does X work?" → Use `rlm_ask` or `rlm_context_query`
- User asks "Where do we do X?" → Use `rlm_multi_project_query` (if Team plan)
- User asks "What are my preferences?" → Use `rlm_recall`
- You need to find code patterns across multiple repos
- You need to understand architecture/documentation

❌ **DON'T use Snipara when:**

- User asks you to read a SPECIFIC file they named → Use native Read tool
- User asks you to edit/write code → Use native Edit/Write tools
- User asks to run commands → Use native Bash tool
- Snipara API returns error → Fall back to native tools

## Recommended Workflow

1. **First query:** Always start with `rlm_ask` (fast, works on Free plan)
2. **If not found:** Try `rlm_context_query` with `search_mode: "semantic"` (requires Pro)
3. **Multi-repo search:** Use `rlm_multi_project_query` if user has Team plan
4. **Remember decisions:** Use `rlm_remember` to store important info for future sessions

## Error Handling

If Snipara returns an error:

- Check if user has required plan (Free/Pro/Team)
- Check if docs are indexed (user needs to upload to dashboard first)
- Fall back to native Read/Grep/Glob tools
- Explain to user what went wrong and suggest solution

## Example Usage

```
User: "How does our authentication system work?"

Good response:
1. Call rlm_ask("authentication system")
2. Get relevant docs in 2 seconds
3. Synthesize answer from returned context

Bad response:
1. Use Grep to search for "auth"
2. Read 10 files sequentially
3. Hit token limits
4. Give incomplete answer
```

---

# Get Started in 2 Minutes

## The Problem You Have Right Now

Your AI assistant searches files one-by-one using grep/find. With large codebases:

- ❌ Queries take 20+ seconds
- ❌ AI reads 50K tokens to answer simple questions
- ❌ You manually search 5 repos to find "how we do X"
- ❌ AI forgets your preferences next session

## The Solution (30 seconds from now)

```bash
# 1. Install
pip install snipara-mcp   # Python
npm install snipara-mcp   # Node.js

# 2. Get your API key
# Sign up at https://snipara.com (Free: 100 queries/month)

# 3. Set environment variable
export SNIPARA_API_KEY="your-key-here"

# 4. Add to your MCP client (Claude Code, Cline, Roo Code, etc.)
# Done! Start using rlm_ask() in your next chat
```

## Your First Query (Try This Now)

```
You: "How does authentication work in my codebase?"

Behind the scenes:
  rlm_context_query("authentication")
  → 2 seconds later
  → Returns top 3 relevant docs (3K tokens instead of 50K)

Result: Instant, accurate answer
```

**Note:** Before querying, index your docs at https://snipara.com/dashboard (upload .md/.txt/.mdx files).

---

## Core Capabilities (Pick What You Need)

### 🎯 Quick Answers (Start Here)

**Plan Required:** ✅ FREE (100 queries/mo)

**Tool:** `rlm_ask`
**Use when:** You need a fast answer from your docs
**Example:** `rlm_ask("API rate limits")`
**Time saved:** 20 seconds → 2 seconds per query

```json
{ "query": "How do we handle webhooks?" }
```

---

### 🔍 Deep Research (Complex Questions)

**Plan Required:** ✅ FREE (keyword only) | 🔥 PRO ($19/mo for semantic)

**Tool:** `rlm_context_query`
**Use when:** You need semantic search with precise token control
**Example:** Find conceptually related content, not just keyword matches
**Benefit:** 90% context reduction (500K → 5K tokens)

```json
{
  "query": "authentication implementation",
  "max_tokens": 6000,
  "search_mode": "hybrid"
}
```

**Search modes by plan:**

- `keyword` - Fast term matching ✅ **FREE**
- `semantic` - Embedding similarity 🔥 **PRO+**
- `hybrid` - Best of both worlds 🔥 **PRO+**

---

### 🌐 Multi-Repo Search

**Plan Required:** 👥 TEAM ($49/mo) or ENTERPRISE

**Tool:** `rlm_multi_project_query`
**Use when:** You have 5+ repos and don't know which has the answer
**Example:** One query searches ALL your team's projects
**Time saved:** 5 minutes of manual searching → 3 seconds

```json
{
  "query": "Where do we send email notifications?",
  "project_ids": [],
  "max_tokens": 8000
}
```

⚠️ **Not available on Free/Pro plans** - Requires Team plan for multi-project access.

---

### 🧠 AI Memory (Remember Preferences)

**Plan Required:** 🔥 PRO ($39/mo Agents) or 👥 TEAM ($79/mo Agents)

**Tools:** `rlm_remember` + `rlm_recall`
**Use when:** You want AI to remember your coding style/decisions
**Benefit:** Consistent code across sessions

**Store a memory:**

```json
{
  "content": "User prefers TypeScript strict mode with functional components",
  "type": "preference",
  "scope": "project"
}
```

**Recall later:**

```json
{
  "query": "What are my coding preferences?",
  "limit": 5
}
```

**Memory types:** `fact`, `decision`, `learning`, `preference`, `todo`, `context`

⚠️ **Requires separate Agents plan** - Memory is part of Agents features, not Context plans.

---

### 👥 Team Standards (Auto-Enforce Rules)

**Plan Required:** 👥 TEAM ($49/mo) or ENTERPRISE

**Tool:** `rlm_shared_context`
**Use when:** Your team needs consistent coding practices
**Setup once:** Upload coding standards to Shared Collection
**Every dev gets:** Auto-injected team rules in every query

```json
{
  "categories": ["MANDATORY", "BEST_PRACTICES"],
  "max_tokens": 4000
}
```

**Categories by priority:**

- `MANDATORY` - Non-negotiable rules (security, architecture)
- `BEST_PRACTICES` - Recommended patterns (40% token budget)
- `GUIDELINES` - Helpful suggestions
- `REFERENCE` - Background info

⚠️ **Not available on Free/Pro plans** - Team-wide features require Team plan.

---

### 🔧 Power User Tools

**Multi-Query (Parallel Searches):**

```json
{
  "queries": [
    { "query": "auth flow", "max_tokens": 3000 },
    { "query": "session management", "max_tokens": 3000 }
  ]
}
```

**Decompose (Break Down Complex Questions):**

```json
{ "query": "Explain the complete payment system architecture" }
```

**Plan (Preview Execution):**

```json
{ "query": "Find all API endpoints", "strategy": "relevance_first" }
```

**Search (Regex Pattern Matching):**

```json
{ "pattern": "async def|async function", "max_results": 20 }
```

**Session Context (Inject Standards):**

```json
{ "context": "Use Python 3.11+, prefer dataclasses over Pydantic" }
```

---

### 📄 Document Management

**Upload Single Doc:**

```json
{ "path": "docs/api.md", "content": "# API Documentation..." }
```

**Bulk Sync (CI/CD Integration):**

```json
{
  "documents": [
    { "path": "docs/auth.md", "content": "..." },
    { "path": "docs/api.md", "content": "..." }
  ],
  "delete_missing": false
}
```

**Check Stats:**

```json
{}
```

---

## ROI Calculator

### Scenario 1: Solo Developer (Large Codebase)

**Current pain:** Grep/find searches take 20+ seconds, read 50K tokens per query

| Metric         | Before Snipara | With Snipara | Savings                  |
| -------------- | -------------- | ------------ | ------------------------ |
| Query speed    | 20 seconds     | 2 seconds    | 18 seconds               |
| Daily queries  | 50             | 50           | -                        |
| Time per day   | 16 minutes     | 1.6 minutes  | **14.4 min/day**         |
| Time per month | 7.2 hours      | 0.72 hours   | **6.5 hours/month**      |
| **Cost**       | **$0**         | **$0-19/mo** | **ROI: 6.5 hours saved** |

**Plan recommendation:** Start with **FREE** (100 queries), upgrade to **PRO** ($19/mo) if you need semantic search.

---

### Scenario 2: Team (5+ Repositories)

**Current pain:** Switch between 5 projects manually, 5 minutes per search

| Metric            | Before Snipara | With Snipara    | Savings                   |
| ----------------- | -------------- | --------------- | ------------------------- |
| Multi-repo search | 5 min          | 3 seconds       | 4.97 min                  |
| Searches per day  | 10             | 10              | -                         |
| Time per day      | 50 minutes     | 30 seconds      | **49.5 min/day**          |
| Time per month    | 24.75 hours    | 0.25 hours      | **24.5 hours/month**      |
| **Cost**          | **$0**         | **$49/mo Team** | **ROI: 24.5 hours saved** |

**Plan recommendation:** **TEAM** ($49/mo) for `rlm_multi_project_query` + shared standards.

---

### Scenario 3: Enterprise (Consistent Standards)

**Current pain:** 10 devs ask "how do we do X?" daily, inconsistent code

| Before                         | With Snipara Shared Context               |
| ------------------------------ | ----------------------------------------- |
| ❌ Each dev googles/asks Slack | ✅ Standards auto-injected in every query |
| ❌ Inconsistent patterns       | ✅ Enforced team conventions              |
| ❌ Onboarding takes 2 weeks    | ✅ New devs get standards instantly       |
| ❌ Code review conflicts       | ✅ Code follows standards from day 1      |

**Cost:** $49/mo Team or $499/mo Enterprise
**ROI:** Consistency + faster onboarding = easily 20+ hours/month saved

---

## Quick Start by Use Case

### Use Case 1: "I have huge docs and grep is slow"

**Plan:** ✅ FREE (100 queries/mo)

```bash
# 1. Index your docs once
Visit https://snipara.com/dashboard → Create project → Upload .md/.txt files

# 2. Query instantly
rlm_ask("How does authentication work?")
```

---

### Use Case 2: "I work on 10 microservices"

**Plan:** 👥 TEAM ($49/mo)

```bash
# 1. Create 10 projects on Snipara dashboard
# 2. Enable Team plan

# 3. Query all repos at once
rlm_multi_project_query("How do we handle rate limiting?")
```

⚠️ **Requires Team plan** - Multi-project search not available on Free/Pro.

---

### Use Case 3: "AI keeps forgetting my preferences"

**Plan:** 🔥 PRO Agents ($39/mo) or 👥 TEAM Agents ($79/mo)

```bash
# 1. Enable Agents plan (separate from Context plan)

# 2. Store your preferences once
rlm_remember(type="preference", content="Use functional React components")

# 3. AI recalls them forever
rlm_recall("my coding preferences")
```

⚠️ **Requires separate Agents subscription** - Memory features not included in Context plans.

---

## Pricing (Two Subscription Types)

### Context Plans (Documentation Search)

| Plan           | Price   | Queries/mo | Search Mode       | Multi-Project |
| -------------- | ------- | ---------- | ----------------- | ------------- |
| **FREE**       | $0      | 100        | Keyword only      | ❌            |
| **PRO**        | $19/mo  | 5,000      | Semantic + Hybrid | ❌            |
| **TEAM**       | $49/mo  | 20,000     | Semantic + Hybrid | ✅            |
| **ENTERPRISE** | $499/mo | Unlimited  | Semantic + Hybrid | ✅            |

### Agents Plans (Memory & Swarms)

| Plan           | Price   | Prerequisite       | Features                    |
| -------------- | ------- | ------------------ | --------------------------- |
| **STARTER**    | $15/mo  | None               | Basic memory (100 memories) |
| **PRO**        | $39/mo  | None               | Unlimited memories, swarms  |
| **TEAM**       | $79/mo  | Context TEAM+      | Team-wide memory sharing    |
| **ENTERPRISE** | $199/mo | Context ENTERPRISE | Advanced coordination       |

⚠️ **Two separate subscriptions:** Context plans for search, Agents plans for memory/swarms.

**Try free first:** 100 queries is ~5 days of usage to test value.

---

## Example Workflows

### Example 1: Quick Answer (FREE plan)

```
User: "What are our API rate limits?"

You call: rlm_ask("API rate limits")

Result: Returns relevant docs in 2 seconds
```

---

### Example 2: Semantic Search (PRO plan)

```
User: "How do we validate user input?"

You call: rlm_context_query("user input validation", search_mode="semantic")

Result: Finds docs about "sanitization", "XSS prevention", "schema validation"
        even if they don't contain exact keywords
```

---

### Example 3: Multi-Repo Search (TEAM plan)

```
User: "Show me all webhook implementations across our projects"

You call: rlm_multi_project_query("webhook implementation")

Result: Returns implementations from all 10 microservices in 3 seconds
```

---

### Example 4: Persistent Memory (PRO Agents plan)

```
Session 1 (Monday):
  User: "I prefer TypeScript strict mode and functional components"
  You call: rlm_remember(type="preference", content="Prefers TS strict + functional")

Session 2 (Friday - NEW SESSION):
  User: "Create a new React component"
  You call: rlm_recall("coding preferences")
  Result: AI remembers to use functional components from Monday!
```

---

### Example 5: Team Standards (TEAM plan)

```
Setup (Admin does once):
  - Upload coding standards to Shared Context Collection
  - Link collection to all team projects

Every developer:
  User: "Write a new API endpoint"
  You call: rlm_shared_context(categories=["MANDATORY"])
  Result: Auto-injects team's API design rules, security requirements, etc.
```

---

## Support & Resources

- **Website:** https://snipara.com
- **Documentation:** https://docs.snipara.com
- **GitHub:** https://github.com/snipara/snipara-mcp
- **Issues:** https://github.com/snipara/snipara-mcp/issues
- **Email:** support@snipara.com

---

## Quick Tips

1. **Start small:** Use `rlm_ask` for quick answers on FREE plan
2. **Upgrade smart:** Get PRO when keyword search isn't finding what you need
3. **Team value:** Multi-project search pays for itself with 5+ repos
4. **Memory requires separate plan:** Context + Agents are two subscriptions
5. **Index first:** Upload docs to dashboard before querying

**When in doubt, start with FREE and upgrade based on value received. 🚀**

---

## Complete Tool Reference (For Power Users)

### Query Tools (All Plans)

**rlm_ask** - Quick keyword search

```json
{ "query": "API rate limits" }
```

**rlm_context_query** - Full-featured semantic search

```json
{
  "query": "authentication",
  "max_tokens": 6000,
  "search_mode": "hybrid",
  "include_metadata": true
}
```

**rlm_search** - Regex pattern search

```json
{
  "pattern": "async def|async function",
  "max_results": 20
}
```

**rlm_inject** - Set session context

```json
{
  "context": "Use Python 3.11+, prefer dataclasses",
  "append": false
}
```

**rlm_context** - Show current session context

```json
{}
```

**rlm_clear_context** - Clear session context

```json
{}
```

---

### Advanced Query Tools (Pro+)

**rlm_multi_query** - Parallel queries

```json
{
  "queries": [
    { "query": "auth flow", "max_tokens": 3000 },
    { "query": "session management", "max_tokens": 3000 }
  ],
  "max_tokens": 8000
}
```

**rlm_decompose** - Break down complex questions

```json
{
  "query": "Explain payment system architecture",
  "max_depth": 2
}
```

**rlm_plan** - Generate execution plan

```json
{
  "query": "Find all API endpoints",
  "strategy": "relevance_first",
  "max_tokens": 16000
}
```

---

### Team Tools (Team+ Plan)

**rlm_multi_project_query** - Search across all repos

```json
{
  "query": "webhook implementation",
  "project_ids": [],
  "exclude_project_ids": [],
  "max_tokens": 8000,
  "per_project_limit": 3
}
```

**rlm_shared_context** - Get team standards

```json
{
  "categories": ["MANDATORY", "BEST_PRACTICES"],
  "max_tokens": 4000,
  "include_content": true
}
```

**rlm_list_templates** - Browse prompt templates

```json
{
  "category": "code-review"
}
```

**rlm_get_template** - Use template with variables

```json
{
  "slug": "security-review",
  "variables": {
    "author": "John",
    "pr_number": "123"
  }
}
```

**rlm_list_collections** - List shared collections

```json
{
  "include_public": true
}
```

**rlm_upload_shared_document** - Upload to shared collection

```json
{
  "collection_id": "col_abc123",
  "title": "TypeScript Standards",
  "content": "# Standards...",
  "category": "BEST_PRACTICES",
  "priority": 90
}
```

---

### Memory Tools (Agents Plan)

**rlm_remember** - Store memory

```json
{
  "content": "User prefers functional components",
  "type": "preference",
  "scope": "project",
  "category": "coding-style",
  "ttl_days": null
}
```

**rlm_recall** - Query memories

```json
{
  "query": "What are my preferences?",
  "type": "preference",
  "limit": 5,
  "min_relevance": 0.5
}
```

**rlm_memories** - List all memories

```json
{
  "type": "preference",
  "category": "coding-style",
  "limit": 20,
  "offset": 0
}
```

**rlm_forget** - Delete memories

```json
{
  "memory_id": "mem_abc123"
}
```

---

### Document Management Tools

**rlm_upload_document** - Upload single doc

```json
{
  "path": "docs/api.md",
  "content": "# API Documentation..."
}
```

**rlm_sync_documents** - Bulk upload

```json
{
  "documents": [
    { "path": "docs/auth.md", "content": "..." },
    { "path": "docs/api.md", "content": "..." }
  ],
  "delete_missing": false
}
```

**rlm_store_summary** - Store document summary

```json
{
  "document_path": "docs/api.md",
  "summary": "RESTful API with OAuth2 auth...",
  "summary_type": "concise",
  "generated_by": "claude-3.5-sonnet"
}
```

**rlm_get_summaries** - Get stored summaries

```json
{
  "document_path": "docs/api.md",
  "summary_type": "concise"
}
```

**rlm_stats** - Get documentation stats

```json
{}
```

**rlm_sections** - List indexed sections

```json
{
  "filter": "auth",
  "limit": 50,
  "offset": 0
}
```

**rlm_read** - Read specific lines

```json
{
  "start_line": 1,
  "end_line": 100
}
```

---

### Advanced Features (Enterprise)

**rlm_swarm_create** - Create agent swarm

```json
{
  "name": "code-review-swarm",
  "description": "Parallel code review",
  "max_agents": 10
}
```

**rlm_swarm_join** - Join swarm

```json
{
  "swarm_id": "swarm_abc123",
  "agent_id": "agent_1",
  "role": "worker",
  "capabilities": ["review", "test"]
}
```

**rlm_claim** - Claim resource for exclusive access

```json
{
  "swarm_id": "swarm_abc123",
  "agent_id": "agent_1",
  "resource_type": "file",
  "resource_id": "src/auth.ts",
  "timeout_seconds": 300
}
```

**rlm_release** - Release claimed resource

```json
{
  "swarm_id": "swarm_abc123",
  "agent_id": "agent_1",
  "claim_id": "claim_abc123"
}
```

**rlm_state_get** - Read swarm state

```json
{
  "swarm_id": "swarm_abc123",
  "key": "progress"
}
```

**rlm_state_set** - Write swarm state

```json
{
  "swarm_id": "swarm_abc123",
  "agent_id": "agent_1",
  "key": "progress",
  "value": { "completed": 5, "total": 10 },
  "expected_version": 1
}
```

**rlm_broadcast** - Broadcast event to swarm

```json
{
  "swarm_id": "swarm_abc123",
  "agent_id": "agent_1",
  "event_type": "task_completed",
  "payload": { "task_id": "task_1" }
}
```

**rlm_task_create** - Create swarm task

```json
{
  "swarm_id": "swarm_abc123",
  "agent_id": "agent_1",
  "title": "Review auth module",
  "description": "Security review",
  "priority": 90
}
```

**rlm_task_claim** - Claim task from queue

```json
{
  "swarm_id": "swarm_abc123",
  "agent_id": "agent_1",
  "task_id": "task_abc123"
}
```

**rlm_task_complete** - Mark task complete

```json
{
  "swarm_id": "swarm_abc123",
  "agent_id": "agent_1",
  "task_id": "task_abc123",
  "success": true,
  "result": { "issues_found": 0 }
}
```

---

## Settings & Configuration

**rlm_settings** - Get project settings

```json
{
  "refresh": false
}
```

Returns current project configuration including:

- Max tokens per query
- Default search mode
- Rate limits
- Enabled features

---

**For complete API documentation, visit: https://docs.snipara.com**
