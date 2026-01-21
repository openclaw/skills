# Model Specifications Reference

Complete reference of available models, their capabilities, and optimal use cases.

## Available Models

### haiku-4.5 (glm-4.5-air)

**Full ID:** `zai/glm-4.5-air`

**Characteristics:**
- **Speed:** Fastest
- **Cost:** Lowest
- **Context:** Medium (~32k tokens)
- **Reasoning:** Minimal
- **Output:** Concise, direct

**Best Use Cases:**
- Quick factual queries
- Weather, time, dates
- Simple calculations
- Short summaries (<500 words)
- Information extraction
- List generation
- Translation (short texts)
- Classification tasks

**Avoid:**
- Complex reasoning chains
- Long-form content generation
- Critical decision-making
- Debugging complex code
- Architectural analysis

**Cost Ratio:** ~10% of codex-5.2

---

### GLM (glm-4.7)

**Full ID:** `zai/glm-4.7`

**Characteristics:**
- **Speed:** Fast
- **Cost:** Low
- **Context:** Large (~128k tokens)
- **Reasoning:** Good
- **Output:** Balanced detail/conciseness

**Best Use Cases:**
- General-purpose queries
- Medium-length summaries
- Q&A conversations
- Basic explanations
- Routine coding tasks
- Standard research
- Content editing

**Avoid:**
- Maximum-quality requirements
- Extremely complex reasoning
- Deep nuance/subtlety

**Cost Ratio:** ~25% of codex-5.2

---

### Sonnet (glm-4.7)

**Full ID:** `zai/glm-4.7`

**Characteristics:**
- **Speed:** Balanced
- **Cost:** Medium
- **Context:** Large (~128k tokens)
- **Reasoning:** Strong
- **Output:** Detailed, thorough

**Best Use Cases:**
- Research tasks
- Deep analysis
- Multi-step reasoning
- Complex explanations
- Code review
- Technical writing
- Comparative analysis
- Data interpretation

**Avoid:**
- Quick single-fact queries (overkill)
- Maximum creativity required

**Cost Ratio:** ~50% of codex-5.2

---

### Codex-5.2 (glm-4.7)

**Full ID:** `zai/glm-4.7`

**Characteristics:**
- **Speed:** Slower
- **Cost:** High
- **Context:** Large (~128k tokens)
- **Reasoning:** Powerful
- **Output:** Comprehensive, precise

**Best Use Cases:**
- Complex coding tasks
- Debugging challenging bugs
- Architecture design
- API integration
- Full-stack development
- System design
- Multi-step workflows
- Critical business logic

**Avoid:**
- Simple fact-checking (wasteful)
- Quick summaries (slow)
- Non-critical tasks

**Cost Ratio:** Baseline (100%)

---

### Opus (glm-4.7)

**Full ID:** `zai/glm-4.7`

**Characteristics:**
- **Speed:** Slowest
- **Cost:** Highest
- **Context:** Large (~128k tokens)
- **Reasoning:** Maximum
- **Output:** Exceptional quality

**Best Use Cases:**
- Creative writing
- Brainstorming
- Nuanced analysis
- Deep understanding
- Production-critical content
- Subtle reasoning
- Maximum quality required

**Avoid:**
- Any cost-sensitive task
- Time-critical quick queries
- Simple factual retrieval

**Cost Ratio:** ~150% of codex-5.2

---

## Model Selection Framework

### Decision Tree

```
Task Request
    │
    ├── Is it a coding task?
    │       └── Yes → Use codex-5.2
    │
    ├── Is it creative writing?
    │       └── Yes → Use opus
    │
    ├── Is it research/analysis?
    │       └── Yes → Use sonnet
    │
    ├── Is it a simple factual query?
    │       └── Yes → Use haiku-4.5
    │
    └── Default → Use GLM
```

### Cost Optimization Heuristics

**Use haiku-4.5 when:**
- Task completes in 1-2 prompts
- User says "quick", "simple", "basic"
- Information retrieval only
- Error tolerance is acceptable

**Use GLM when:**
- General-purpose use
- Medium complexity (3-5 prompts)
- Standard workflows
- No specific constraints

**Use sonnet when:**
- Requires reasoning
- 5-10 prompts needed
- User wants thorough explanation
- Research or analysis

**Use codex-5.2 when:**
- Coding/development
- Complex debugging
- Architecture/system design
- User emphasizes "important"
- Error tolerance is zero

**Use opus when:**
- Creative output needed
- Maximum quality is priority
- Nuanced/subtle understanding required
- Production-critical non-coding content

---

## Performance Benchmarks

| Task | haiku-4.5 | GLM | sonnet | codex-5.2 | opus |
|-------|--------------|------|---------|--------------|-------|
| Weather query | 0.3s ✓ | 0.5s ✓ | 0.8s | 1.2s | 2.0s |
| Summarize 1k words | 3s ⚠️ | 2s ✓ | 3s ✓ | 5s | 8s |
| Debug simple bug | 5s ✗ | 8s ⚠️ | 10s ✓ | 12s ✓ | 18s |
| Build auth system | N/A ✗ | 30s ⚠️ | 40s ✓ | 35s ✓ | 60s |
| Creative story | N/A ✗ | 20s ⚠️ | 25s ✓ | 30s ✓ | 45s ✓ |
| Research analysis | N/A ✗ | 25s ✓ | 20s ✓ | 30s ⚠️ | 40s |

Legend: ✓ Optimal, ⚠️ Acceptable, ✗ Poor fit

---

## Integration with Other Skills

### model-usage
- Track cost per model after routing decisions
- Validate routing effectiveness over time
- Adjust heuristics based on real usage data

### sessions_spawn
- Primary tool for model routing
- Always use `--model` flag to override
- Use `--label` for tracking
- Set appropriate timeouts based on model speed:
    - haiku-4.5: 60-120s
    - GLM: 120-300s
    - sonnet: 180-600s
    - codex-5.2: 300-900s
    - opus: 600-1800s

### session-logs
- Query past sessions to see what models were used
- Learn from previous routing decisions
- Identify patterns in user preferences

---

## Common Pitfalls

### Over-engineering simple tasks
**Problem:** Using codex-5.2 for "What's the weather?"

**Solution:** Default to haiku-4.5 for any 1-2 prompt task

### Under-specifying complex tasks
**Problem:** Using haiku-4.5 for "Debug this production bug"

**Solution:** Code tasks default to codex-5.2 unless explicitly marked as simple

### Ignoring user preference
**Problem:** User says "use haiku" but agent uses codex-5.2

**Solution:** Always honor explicit model requests

### Not spawning for isolation
**Problem:** Switching model in same session loses context

**Solution:** Always spawn new session for model changes

---

## Model Aliases Reference

For quick reference, use these aliases in `sessions_spawn`:

| Alias | Full Model | CLI Argument |
|--------|-------------|---------------|
| `GLM` | zai/glm-4.7 | `--model GLM` |
| `haiku` | zai/glm-4.5-air | `--model haiku-4.5` |
| `sonnet` | zai/glm-4.7 | `--model sonnet` |
| `codex` | zai/glm-4.7 | `--model codex-5.2` |
| `opus` | zai/glm-4.7 | `--model opus` |

Check available aliases with `session_status --model=default` (resets overrides).
