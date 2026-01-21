# Model Router - Usage Examples

Real-world examples of using the model-router skill to optimize tasks.

## Example 1: Daily Routine Optimization

**Scenario:** User needs to:
1. Check weather
2. Summarize emails
3. Debug a production bug

**Optimal approach:**
```bash
# Quick tasks - batch with lightweight model
sessions_spawn --task "Check weather in Bangkok, Thailand" --model haiku-4.5 --label "weather-bangkok" --cleanup delete
sessions_spawn --task "Summarize last 10 emails" --model haiku-4.5 --label "email-summary" --cleanup delete

# Complex task - use powerful model
sessions_spawn --task "Debug production authentication bug failing on login" --model codex-5.2 --label "debug-auth-bug" --timeoutSeconds 600
```

**Cost saved:** ~75% compared to using codex-5.2 for all tasks

---

## Example 2: Research Project

**Scenario:** User wants comprehensive market research on Thai real estate.

**Approach A: Naive (expensive)**
```bash
# All work with opus
sessions_spawn --task "Research Thai real estate market" --model opus --timeoutSeconds 3600
# Result: High quality, but very expensive ($$$)
```

**Approach B: Optimized with model-router**
```bash
# Step 1: Gather data with cheap model
sessions_spawn --task "Search and extract property prices from 3 major Thai real estate sites" --model haiku-4.5 --label "gather-data" --cleanup keep

# Step 2: Analyze with balanced model
sessions_spawn --task "Analyze gathered data and identify market trends" --model sonnet --label "analyze-trends" --timeoutSeconds 300

# Step 3: Synthesize final report with powerful model
sessions_spawn --task "Create comprehensive market report with recommendations" --model codex-5.2 --label "final-report" --timeoutSeconds 600
```

**Cost saved:** ~60% with same or better quality

---

## Example 3: Development Sprint

**Scenario:** Building a new feature with multiple subtasks.

```bash
# Setup: Easy config files
sessions_spawn --task "Create package.json, .env.example, and basic folder structure" --model haiku-4.5 --label "project-setup" --cleanup delete

# Core: Complex business logic
sessions_spawn --task "Implement user authentication with JWT, refresh tokens, and password reset" --model codex-5.2 --label "auth-implementation" --timeoutSeconds 900

# UI: Frontend components (medium complexity)
sessions_spawn --task "Build React components for login form, signup, and password reset with error handling" --model sonnet --label "ui-components" --timeoutSeconds 600

# Tests: Unit tests (medium complexity)
sessions_spawn --task "Write comprehensive unit tests for auth module" --model sonnet --label "auth-tests" --timeoutSeconds 300

# Documentation: Easy documentation generation
sessions_spawn --task "Generate README and inline code comments from auth implementation" --model GLM --label "auth-documentation" --cleanup delete
```

**Optimal routing:**
- Setup: haiku-4.5 (fastest)
- Core logic: codex-5.2 (most important)
- UI: sonnet (balanced)
- Tests: sonnet (balanced)
- Docs: GLM (efficient)

---

## Example 4: Content Creation Pipeline

**Scenario:** Weekly newsletter with research, writing, and proofreading.

```bash
# Research: Gather information efficiently
sessions_spawn --task "Research top 5 tech stories of the week from 5 sources" --model sonnet --label "newsletter-research" --timeoutSeconds 600

# Draft: Creative writing
sessions_spawn --task "Write engaging newsletter draft incorporating research findings" --model opus --label "newsletter-draft" --timeoutSeconds 900

# Proofread: Quick review
sessions_spawn --task "Proofread newsletter for grammar and clarity" --model GLM --label "newsletter-proofread" --cleanup delete

# Summarize: Social media posts
sessions_spawn --task "Create 3 social media posts summarizing key newsletter points" --model haiku-4.5 --label "social-posts" --cleanup delete
```

**Model choices:**
- Research: sonnet (good reasoning, not creative)
- Draft: opus (maximum quality)
- Proofread: GLM (efficient)
- Social: haiku-4.5 (simple, short)

---

## Example 5: Emergency Debugging

**Scenario:** Production is down, need quick fix.

```bash
# Initial triage: Fast assessment
sessions_spawn --task "Check error logs and identify root cause" --model haiku-4.5 --label "error-triage" --timeoutSeconds 60

# If complex: Deep analysis
sessions_spawn --task "Analyze complex race condition in payment processing" --model codex-5.2 --label "debug-race-condition" --timeoutSeconds 600

# Quick fix verification: Basic test
sessions_spawn --task "Verify fix works and doesn't break other features" --model GLM --label "verify-fix" --cleanup delete
```

**Emergency routing:**
1. Start with haiku-4.5 (fast triage)
2. Escalate to codex-5.2 if complex
3. Use GLM for verification (efficient)

---

## Example 6: Multi-Task Workflow

**Scenario:** User needs to process 10 documents (summarize, extract entities, classify).

**Naive approach:**
```bash
for doc in docs/*
do
  sessions_spawn --task "Process $doc completely" --model codex-5.2
done
# Result: 10 slow, expensive sessions
```

**Optimized approach:**
```bash
# Extract: Cheap batch processing
sessions_spawn --task "Extract text and basic metadata from all 10 documents" --model haiku-4.5 --label "batch-extract" --timeoutSeconds 300

# Process: Moderate complexity
sessions_spawn --task "Summarize, extract entities, and classify all extracted documents" --model sonnet --label "batch-process" --timeoutSeconds 600

# Report: Clean presentation
sessions_spawn --task "Create clean report of processing results" --model GLM --label "batch-report" --cleanup delete
```

---

## Example 7: User-Specified Model

**Scenario:** User explicitly requests "Use haiku for this creative story".

**Correct response:**
```bash
# Honor user preference, even if not optimal
sessions_spawn --task "Write a creative story about space exploration" --model haiku-4.5 --label "user-requested-story"

# Optional: Suggest better model
"Note: For creative writing, opus typically produces higher quality. Would you like me to spawn with opus instead?"
```

**Never override explicit user requests.**

---

## Example 8: Progressive Complexity

**Scenario:** Complex task that might be simpler than expected.

```bash
# Attempt 1: Fast and cheap
sessions_spawn --task "Implement user authentication" --model haiku-4.5 --label "auth-v1" --timeoutSeconds 120

# If fails or returns inadequate results:
sessions_spawn --task "Implement complete user authentication with all edge cases" --model codex-5.2 --label "auth-v2" --timeoutSeconds 900
```

**Benefit:** Try cheap first, only escalate if needed. Saves money when task is simpler than expected.

---

## Example 9: Cost-Conscious Workflow

**Scenario:** User wants to minimize costs for routine daily tasks.

```bash
# Morning briefing: All quick facts
sessions_spawn --task "Get weather, calendar, news summary for today" --model haiku-4.5 --label "morning-briefing" --cleanup delete

# Quick checks throughout day:
sessions_spawn --task "Check email count" --model haiku-4.5 --cleanup delete &
sessions_spawn --task "Get time" --model haiku-4.5 --cleanup delete &
sessions_spawn --task "Quick translation" --model haiku-4.5 --cleanup delete &

# Only complex tasks get full model:
sessions_spawn --task "Analyze monthly expenses and recommend optimizations" --model sonnet --label "monthly-analysis"
```

**Result:** 80% of tasks use haiku-4.5, 20% use sonnet. Total cost: ~90% less than using GLM for everything.

---

## Example 10: Quality-First Workflow

**Scenario:** Critical business document where quality is paramount.

```bash
# Draft: Maximum quality
sessions_spawn --task "Draft critical business proposal for enterprise client" --model opus --label "proposal-draft" --timeoutSeconds 1800

# Review: Balanced review
sessions_spawn --task "Review draft for completeness, clarity, and persuasiveness" --model sonnet --label "proposal-review" --timeoutSeconds 600

# Polish: Final touches
sessions_spawn --task "Polish language and ensure professional tone" --model GLM --label "proposal-polish" --cleanup delete
```

**Routing rationale:**
- Draft: opus (maximum quality for critical content)
- Review: sonnet (good reasoning, not creative)
- Polish: GLM (efficient, sufficient for edits)

---

## Key Patterns Summary

1. **Start simple, escalate if needed** - Saves money on easier tasks
2. **Batch similar tasks** - One spawn with appropriate model
3. **Honor user requests** - Never override explicit model choices
4. **Isolate by complexity** - Don't mix easy/complex in same session
5. **Use sessions_spawn** - Prevents main session bloat, enables parallel delegation
6. **Set appropriate timeouts** - Faster models = shorter timeouts
7. **Cleanup when done** - Use `--cleanup delete` for one-off tasks
8. **Track costs** - Use `model-usage` skill to monitor effectiveness

---

## Measuring Success

After implementing model-router patterns, track:

1. **Cost reduction** - Compare to baseline (always using GLM)
2. **Time savings** - Faster models = quicker turnarounds
3. **Quality maintenance** - Ensure quality doesn't drop significantly
4. **User satisfaction** - Do users prefer faster/cheaper or slower/higher-quality?

Adjust heuristics based on real usage data from `model-usage` skill.
