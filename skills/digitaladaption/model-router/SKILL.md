---
name: model-router
description: A comprehensive AI model routing system that automatically selects the optimal model for any task. Set up multiple AI providers (Anthropic, OpenAI, Gemini, Moonshot, Z.ai, GLM) with secure API key storage, then route tasks to the best model based on task type, complexity, and cost optimization. Includes interactive setup wizard, task classification, and cost-effective delegation patterns. Use when you need "use X model for this", "switch model", "optimal model", "which model should I use", or to balance quality vs cost across multiple AI providers.
version: 1.1.0
---

# Model Router

**Intelligent AI model routing across multiple providers for optimal cost-performance balance.**

Automatically select the best model for any task based on complexity, type, and your preferences. Support for 6 major AI providers with secure API key management and interactive configuration.

## 🎯 What It Does

- **Analyzes tasks** and classifies them by type (coding, research, creative, simple, etc.)
- **Routes to optimal models** from your configured providers
- **Optimizes costs** by using cheaper models for simple tasks
- **Secures API keys** with file permissions (600) and isolated storage
- **Provides recommendations** with confidence scoring and reasoning

## 🚀 Quick Start

### Step 1: Run the Setup Wizard

```bash
cd skills/model-router
python3 scripts/setup-wizard.py
```

The wizard will guide you through:
1. **Provider setup** - Add your API keys (Anthropic, OpenAI, Gemini, etc.)
2. **Task mappings** - Choose which model for each task type
3. **Preferences** - Set cost optimization level

### Step 2: Use the Classifier

```bash
# Get model recommendation for a task
python3 scripts/classify_task.py "Build a React authentication system"

# Output:
# Recommended Model: claude-sonnet
# Confidence: 85%
# Cost Level: medium
# Reasoning: Matched 2 keywords: build, system
```

### Step 3: Route Tasks with Sessions

```bash
# Spawn with recommended model
sessions_spawn --task "Debug this memory leak" --model claude-sonnet

# Use aliases for quick access
sessions_spawn --task "What's the weather?" --model haiku
```

## 📊 Supported Providers

| Provider | Models | Best For | Key Format |
|----------|--------|----------|------------|
| **Anthropic** | claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5 | Coding, reasoning, creative | `sk-ant-...` |
| **OpenAI** | gpt-4o, gpt-4o-mini, o1-mini, o1-preview | Tools, deep reasoning | `sk-proj-...` |
| **Gemini** | gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash | Multimodal, huge context (2M) | `AIza...` |
| **Moonshot** | moonshot-v1-8k/32k/128k | Chinese language | `sk-...` |
| **Z.ai** | glm-4.5-air, glm-4.7 | Cheapest, fast | Various |
| **GLM** | glm-4-flash, glm-4-plus, glm-4-0520 | Chinese, coding | `ID.secret` |

## 🎛️ Task Type Mappings

Default routing (customizable via wizard):

| Task Type | Default Model | Why |
|-----------|---------------|-----|
| `simple` | glm-4.5-air | Fastest, cheapest for quick queries |
| `coding` | claude-sonnet-4-5 | Excellent code understanding |
| `research` | claude-sonnet-4-5 | Balanced depth and speed |
| `creative` | claude-opus-4-5 | Maximum creativity |
| `math` | o1-mini | Specialized reasoning |
| `vision` | gemini-1.5-flash | Fast multimodal |
| `chinese` | glm-4.7 | Optimized for Chinese |
| `long_context` | gemini-1.5-pro | Up to 2M tokens |

## 💰 Cost Optimization

### Aggressive Mode
Always uses the cheapest capable model:
- Simple → glm-4.5-air (~10% cost)
- Coding → claude-haiku-4-5 (~25% cost)
- Research → claude-sonnet-4-5 (~50% cost)

**Savings:** 50-90% compared to always using premium models

### Balanced Mode (Default)
Considers cost vs quality:
- Simple tasks → Cheap models
- Critical tasks → Premium models
- Automatic escalation if cheap model fails

### Quality Mode
Always uses the best model regardless of cost

## 🔒 Security

### API Key Storage
```
~/.model-router/
├── config.json       # Model mappings (chmod 600)
└── .api-keys         # API keys (chmod 600)
```

**Features:**
- File permissions restricted to owner (600)
- Isolated from version control
- Encrypted at rest (via OS filesystem encryption)
- Never logged or printed

### Best Practices
1. **Never commit** `.api-keys` to version control
2. **Use environment variables** for production deployments
3. **Rotate keys** regularly via the wizard
4. **Audit access** with `ls -la ~/.model-router/`

## 📖 Usage Examples

### Example 1: Cost-Optimized Workflow

```bash
# Classify task first
python3 scripts/classify_task.py "Extract prices from this CSV"

# Result: simple task → use glm-4.5-air
sessions_spawn --task "Extract prices" --model glm-4.5-air

# Then analyze with better model if needed
sessions_spawn --task "Analyze price trends" --model claude-sonnet
```

### Example 2: Progressive Escalation

```bash
# Try cheap model first (60s timeout)
sessions_spawn --task "Fix this bug" --model glm-4.5-air --runTimeoutSeconds 60

# If fails, escalate to premium
sessions_spawn --task "Fix complex architecture bug" --model claude-opus
```

### Example 3: Parallel Processing

```bash
# Batch simple tasks in parallel with cheap model
sessions_spawn --task "Summarize doc A" --model glm-4.5-air &
sessions_spawn --task "Summarize doc B" --model glm-4.5-air &
sessions_spawn --task "Summarize doc C" --model glm-4.5-air &
wait
```

### Example 4: Multimodal with Gemini

```bash
# Vision task with 2M token context
sessions_spawn --task "Analyze these 100 images" --model gemini-1.5-pro
```

## 🛠️ Configuration Files

### `~/.model-router/config.json`
```json
{
  "version": "1.1.0",
  "providers": {
    "anthropic": {
      "configured": true,
      "models": ["claude-opus-4-5", "claude-sonnet-4-5", "claude-haiku-4-5"]
    },
    "openai": {
      "configured": true,
      "models": ["gpt-4o", "gpt-4o-mini", "o1-mini", "o1-preview"]
    }
  },
  "task_mappings": {
    "simple": "glm-4.5-air",
    "coding": "claude-sonnet-4-5",
    "research": "claude-sonnet-4-5",
    "creative": "claude-opus-4-5"
  },
  "preferences": {
    "cost_optimization": "balanced",
    "default_provider": "anthropic"
  }
}
```

### `~/.model-router/.api-keys`
```bash
# Generated by setup wizard - DO NOT edit manually
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
GEMINI_API_KEY=AIza...
```

## 🔄 Version 1.1 Changes

### New Features
- ✅ **Interactive setup wizard** for guided configuration
- ✅ **Secure API key storage** with file permissions
- ✅ **Task-to-model mapping** customization
- ✅ **Multi-provider support** (6 providers)
- ✅ **Cost optimization levels** (aggressive/balanced/quality)

### Improvements
- ✅ Better task classification with confidence scores
- ✅ Provider-specific model recommendations
- ✅ Enhanced security with isolated storage
- ✅ Comprehensive documentation

### Migration from 1.0
Run the setup wizard to reconfigure:
```bash
python3 scripts/setup-wizard.py
```

## 📚 Command Reference

### Setup Wizard
```bash
python3 scripts/setup-wizard.py
```
Interactive configuration of providers, mappings, and preferences.

### Task Classifier
```bash
python3 scripts/classify_task.py "your task description"
python3 scripts/classify_task.py "your task" --format json
```
Get model recommendation with reasoning.

### List Models
```bash
python3 scripts/setup-wizard.py --list
```
Show all available models and their status.

## 🤝 Integration with Other Skills

| Skill | Integration |
|-------|-------------|
| **model-usage** | Track cost per provider to optimize routing |
| **sessions_spawn** | Primary tool for model delegation |
| **session_status** | Check current model and usage |

## ⚡ Performance Tips

1. **Start simple** - Try cheap models first
2. **Batch tasks** - Combine multiple simple tasks
3. **Use cleanup** - Delete sessions after one-off tasks
4. **Set timeouts** - Prevent runaway sub-agents
5. **Monitor usage** - Track costs per provider

## 🐛 Troubleshooting

### "No suitable model found"
- Run setup wizard to configure providers
- Check API keys are valid
- Verify permissions on `.api-keys` file

### "Module not found"
```bash
pip3 install -r requirements.txt  # if needed
```

### Wrong model selected
1. Customize task mappings via wizard
2. Use explicit model in `sessions_spawn --model`
3. Adjust cost optimization preference

## 📖 Additional Resources

- **Provider Docs:**
  - [Anthropic](https://docs.anthropic.com)
  - [OpenAI](https://platform.openai.com/docs)
  - [Gemini](https://ai.google.dev/docs)
  - [Moonshot](https://platform.moonshot.cn/docs)
  - [Z.ai](https://api.z.ai/docs)
  - [GLM](https://open.bigmodel.cn/dev/api)

- **Setup:** Run `python3 scripts/setup-wizard.py`
- **Support:** Check `references/` folder for detailed guides
