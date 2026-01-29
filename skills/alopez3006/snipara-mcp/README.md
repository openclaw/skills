# Snipara MCP

[![PyPI version](https://badge.fury.io/py/snipara-mcp.svg)](https://pypi.org/project/snipara-mcp/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Model Context Protocol (MCP) server for [Snipara](https://snipara.com) - Context optimization and Agent infrastructure for LLMs.**

![Snipara MCP Demo](https://snipara.com/images/mcp-demo.gif)

## Overview

Snipara MCP is a client package that connects AI assistants to the [Snipara API](https://snipara.com), enabling:

- **🔍 90% Context Reduction** - Query 500K tokens, get 5K relevant results
- **🌐 Multi-Project Search** - Search across all your repos in one query
- **🧠 AI Memory** - Persistent semantic memory across sessions
- **👥 Team Standards** - Auto-inject coding standards into every query
- **🤖 Multi-Agent Swarms** - Coordinate multiple AI agents with shared state

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│  Your AI Assistant (Claude, GPT, Cursor, etc.)                 │
│  ├── Asks: "How does authentication work?"                     │
│  └── Uses: rlm_context_query("authentication")                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │  Snipara MCP      │  (This package)
                   │  Client Library   │
                   └─────────┬─────────┘
                             │ HTTPS
                             ▼
                   ┌─────────────────────┐
                   │  Snipara API        │
                   │  api.snipara.com    │
                   │  - Indexed docs     │
                   │  - Semantic search  │
                   │  - Agent memory     │
                   └─────────┬───────────┘
                             │
                   ┌─────────▼─────────┐
                   │  Returns: 3K      │
                   │  relevant tokens  │
                   │  instead of 50K   │
                   └───────────────────┘
```

**Key Insight:** This is the **client package** - it connects to Snipara's API to fetch optimized context. The server-side implementation is private.

## What's In This Repository

This is the **open-source MCP client package** published to PyPI as [`snipara-mcp`](https://pypi.org/project/snipara-mcp/).

```
snipara-mcp/
├── src/snipara_mcp/
│   ├── __init__.py         # Package entry point
│   ├── server.py           # MCP stdio transport (2,050 lines)
│   ├── rlm_tools.py        # 39 tool implementations (2,117 lines)
│   └── auth.py             # OAuth device flow (402 lines)
├── skill.md                # ClawdHub marketplace documentation
├── pyproject.toml          # PyPI package configuration
└── README.md               # This file
```

**What's NOT in this repo (private):**
- FastAPI backend server
- Database models and search algorithms
- Rate limiting and billing logic
- Internal API endpoints

## Quick Start

### Installation

**Option 1: uvx (No Install Required)**
```bash
uvx snipara-mcp
```

**Option 2: pip**
```bash
pip install snipara-mcp
```

**Option 3: With RLM Runtime**
```bash
pip install snipara-mcp[rlm]
```

### Configuration

Get your API key from [snipara.com/dashboard](https://snipara.com/dashboard)

#### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "snipara": {
      "command": "uvx",
      "args": ["snipara-mcp"],
      "env": {
        "SNIPARA_API_KEY": "rlm_your_key",
        "SNIPARA_PROJECT_ID": "your_project_id"
      }
    }
  }
}
```

#### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "snipara": {
      "command": "uvx",
      "args": ["snipara-mcp"],
      "env": {
        "SNIPARA_API_KEY": "rlm_your_key",
        "SNIPARA_PROJECT_ID": "your_project_id"
      }
    }
  }
}
```

#### Claude Code

```bash
claude mcp add snipara -- uvx snipara-mcp
export SNIPARA_API_KEY="rlm_your_key"
export SNIPARA_PROJECT_ID="your_project_id"
```

#### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "snipara": {
      "command": "uvx",
      "args": ["snipara-mcp"],
      "env": {
        "SNIPARA_API_KEY": "rlm_your_key",
        "SNIPARA_PROJECT_ID": "your_project_id"
      }
    }
  }
}
```

### Your First Query

Once configured, ask your AI:

> "Use snipara to find how authentication works"

Behind the scenes:
```
rlm_context_query("authentication")
→ 2 seconds later
→ Returns top 3 relevant docs (3K tokens instead of 50K)
```

## Features

### 🎯 Context Optimization (All Plans)

**Tools:** `rlm_context_query`, `rlm_ask`, `rlm_search`

Query your documentation with semantic search and get only relevant results within your token budget.

```json
{
  "query": "authentication implementation",
  "max_tokens": 6000,
  "search_mode": "hybrid"
}
```

### 🌐 Multi-Project Search (Team+)

**Tool:** `rlm_multi_project_query`

Search across all your team's repositories in one query.

```json
{
  "query": "How do we handle webhooks?",
  "project_ids": [],
  "max_tokens": 8000
}
```

### 🧠 AI Memory (Agents Plans)

**Tools:** `rlm_remember`, `rlm_recall`

Persistent semantic memory across sessions with confidence decay.

```json
// Store once
{
  "content": "User prefers TypeScript strict mode",
  "type": "preference",
  "scope": "project"
}

// Recall later
{
  "query": "What are my coding preferences?",
  "limit": 5
}
```

### 👥 Team Standards (Team+)

**Tool:** `rlm_shared_context`

Auto-inject team coding standards into every query.

```json
{
  "categories": ["MANDATORY", "BEST_PRACTICES"],
  "max_tokens": 4000
}
```

### 🤖 Multi-Agent Swarms (Enterprise)

**Tools:** `rlm_swarm_create`, `rlm_claim`, `rlm_task_create`, etc.

Coordinate multiple AI agents with:
- Shared state management
- Resource claims (prevent conflicts)
- Distributed task queue
- Event broadcasting

```json
// Create swarm
{ "name": "code-review-swarm", "max_agents": 5 }

// Claim file access
{ "swarm_id": "...", "resource_type": "file", "resource_id": "src/auth.ts" }

// Create task
{ "swarm_id": "...", "title": "Review auth module", "priority": 90 }
```

## Complete Tool Reference

### Primary Tools
- **rlm_context_query** - Semantic search with token budget
- **rlm_ask** - Quick keyword search
- **rlm_search** - Regex pattern search

### Advanced Tools
- **rlm_multi_query** - Parallel queries
- **rlm_decompose** - Break down complex questions
- **rlm_plan** - Generate execution plan
- **rlm_inject** - Set session context

### Team Tools
- **rlm_multi_project_query** - Cross-repo search
- **rlm_shared_context** - Team standards
- **rlm_list_templates** - Prompt templates
- **rlm_upload_shared_document** - Upload team docs

### Memory Tools (Agents Plan)
- **rlm_remember** - Store memory
- **rlm_recall** - Semantic recall
- **rlm_memories** - List all memories
- **rlm_forget** - Delete memories

### Swarm Tools (Enterprise)
- **rlm_swarm_create** / **rlm_swarm_join**
- **rlm_claim** / **rlm_release**
- **rlm_state_get** / **rlm_state_set**
- **rlm_broadcast**
- **rlm_task_create** / **rlm_task_claim** / **rlm_task_complete**

### Document Management
- **rlm_upload_document** - Upload single doc
- **rlm_sync_documents** - Bulk sync
- **rlm_store_summary** - Store LLM-generated summary
- **rlm_stats** - Documentation statistics

**Total:** 39 tools

Full documentation: [docs.snipara.com](https://docs.snipara.com)

## Pricing

### Context Plans (Documentation Search)

| Plan       | Price   | Queries/mo | Search Mode       | Multi-Project |
| ---------- | ------- | ---------- | ----------------- | ------------- |
| FREE       | $0      | 100        | Keyword only      | ❌            |
| PRO        | $19/mo  | 5,000      | Semantic + Hybrid | ❌            |
| TEAM       | $49/mo  | 20,000     | Semantic + Hybrid | ✅            |
| ENTERPRISE | $499/mo | Unlimited  | Semantic + Hybrid | ✅            |

### Agents Plans (Memory & Swarms)

| Plan       | Price   | Features                                    |
| ---------- | ------- | ------------------------------------------- |
| STARTER    | $15/mo  | Basic memory (100 memories)                 |
| PRO        | $39/mo  | Unlimited memories, swarms                  |
| TEAM       | $79/mo  | Team-wide memory (requires Context TEAM+)   |
| ENTERPRISE | $199/mo | Advanced coordination (requires Context ENT |

**Note:** Context and Agents are separate subscriptions.

## Development

### Prerequisites

- Python 3.10+
- pip or uv

### Local Setup

```bash
# Clone the repo
git clone https://github.com/alopez3006/snipara-mcp.git
cd snipara-mcp

# Install dependencies
pip install -e .

# Set environment variables
export SNIPARA_API_KEY="rlm_your_key"
export SNIPARA_PROJECT_ID="your_project_id"

# Test the package
python -m snipara_mcp
```

### Project Structure

```
src/snipara_mcp/
├── __init__.py         # Package entry point, CLI main()
├── server.py           # MCP stdio transport implementation
│                       # - Handles MCP protocol (JSON-RPC)
│                       # - Tool registration and dispatch
│                       # - Prompt auto-injection
│
├── rlm_tools.py        # 39 tool implementations
│                       # - Context optimization tools
│                       # - Agent memory tools
│                       # - Multi-agent swarm tools
│                       # - Document management
│
└── auth.py             # OAuth device flow authentication
                        # - Login/logout/status CLI commands
                        # - Token storage and refresh
```

### Testing

```bash
# Test basic connection
uvx snipara-mcp

# Test with specific tool
echo '{"query": "test"}' | uvx snipara-mcp

# Test OAuth flow
snipara-mcp-login
snipara-mcp-status
```

### Publishing to PyPI

```bash
# Bump version in pyproject.toml
# version = "2.2.1"

# Build distribution
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

## Architecture

### MCP Protocol

This package implements the [Model Context Protocol](https://modelcontextprotocol.io/) stdio transport:

```
AI Client → stdin → snipara-mcp → HTTPS → api.snipara.com
AI Client ← stdout ← snipara-mcp ← JSON ← api.snipara.com
```

### Authentication

Supports two authentication methods:

1. **API Key** (Recommended)
   ```bash
   export SNIPARA_API_KEY="rlm_..."
   ```

2. **OAuth Device Flow**
   ```bash
   snipara-mcp-login
   # Follow browser prompt to authorize
   ```

Tokens are stored in `~/.snipara/credentials.json`

### Rate Limiting

Rate limits are enforced server-side based on your plan:
- FREE: 100 queries/month
- PRO: 5,000 queries/month
- TEAM: 20,000 queries/month
- ENTERPRISE: Unlimited

## Upgrading

When a new version is released:

### 1. Clear uvx cache
```bash
# macOS/Linux
rm -rf ~/.cache/uv/tools/snipara-mcp
rm -rf ~/Library/Caches/uv/tools/snipara-mcp

# Windows
rmdir /s %LOCALAPPDATA%\uv\tools\snipara-mcp
```

### 2. Restart your MCP client

MCP tool definitions are loaded at startup. Restart Claude Desktop, Cursor, or your MCP client.

### 3. Verify version

```bash
snipara-mcp-status
```

## Troubleshooting

### MCP tools not showing up

1. **Restart your MCP client** - Tools are cached at startup
2. **Clear uvx cache** - See Upgrading section
3. **Check config syntax** - Ensure valid JSON in MCP config

### "Invalid API key" error

- Verify API key in [dashboard](https://snipara.com/dashboard)
- Check for whitespace in config
- Try OAuth: `snipara-mcp-login`

### MCP server not connecting

- Check `uvx` is installed: `uvx --version`
- Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Check Claude Code output panel for errors

## RLM Runtime Integration

Use Snipara tools programmatically in Python:

```python
from rlm import RLM

# Snipara tools auto-registered when credentials set
rlm = RLM(
    model="claude-sonnet-4-20250514",
    snipara_api_key="rlm_your_key",
    snipara_project_slug="your-project"
)

# LLM can now query your docs during execution
result = rlm.run("Implement auth following our coding standards")
```

See: [rlm-runtime documentation](https://github.com/alopez3006/rlm-runtime)

## CI/CD Integration

Auto-sync docs on git push:

```bash
curl -X POST "https://api.snipara.com/v1/YOUR_PROJECT/webhook/sync" \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"path": "docs/api.md", "content": "..."}]}'
```

See: [GitHub Action example](#) (coming soon)

## Support

- **Website:** [snipara.com](https://snipara.com)
- **Documentation:** [docs.snipara.com](https://docs.snipara.com)
- **Issues:** [GitHub Issues](https://github.com/alopez3006/snipara-mcp/issues)
- **Email:** support@snipara.com
- **Discord:** [Join our community](https://discord.gg/snipara)

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

**Development Guidelines:**
- Follow existing code style
- Add docstrings to public functions
- Update README if adding features
- Test with multiple MCP clients

## Version History

| Version | Date       | Changes                                             |
| ------- | ---------- | --------------------------------------------------- |
| 2.2.0   | 2026-01-29 | Separate public repository, update repo URL         |
| 2.1.0   | 2025-01-25 | Full tool parity with FastAPI (39 tools)            |
| 1.8.1   | 2025-01-25 | Add multi_project_query for cross-repo search       |
| 1.7.6   | 2025-01-24 | Redis URL protocol support                          |
| 1.7.0   | 2025-01-21 | OAuth device flow authentication                    |
| 1.6.0   | 2025-01-20 | Agent Memory and Multi-Agent Swarms (14 new tools)  |
| 1.5.0   | 2025-01-18 | Auto-inject Snipara usage instructions              |
| 1.4.0   | 2025-01-15 | RLM Runtime integration                             |
| 1.3.0   | 2025-01-10 | Shared Context tools (Team+)                        |
| 1.2.0   | 2025-01-05 | Document upload and sync tools                      |
| 1.0.0   | 2024-12-15 | Initial release with core context optimization      |

## License

MIT License - see [LICENSE](LICENSE) file

---

**Built with ❤️ by the Snipara team**

[Website](https://snipara.com) • [Documentation](https://docs.snipara.com) • [PyPI](https://pypi.org/project/snipara-mcp/) • [GitHub](https://github.com/alopez3006/snipara-mcp)
