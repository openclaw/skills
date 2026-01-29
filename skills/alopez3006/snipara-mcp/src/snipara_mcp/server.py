#!/usr/bin/env python3
"""
Snipara MCP Server - stdio transport to Snipara REST API.

This MCP server connects your LLM client (Claude Desktop, Cursor, etc.)
to your Snipara project for context-optimized documentation queries.

Usage:
    snipara-mcp

Authentication (in priority order):
    1. OAuth token from ~/.snipara/tokens.json (run: snipara-mcp-login)
    2. SNIPARA_API_KEY environment variable (legacy)

Environment variables:
    SNIPARA_PROJECT_ID: Your project ID (required if not using OAuth)
    SNIPARA_API_KEY: Your Snipara API key (legacy, optional if using OAuth)
    SNIPARA_API_URL: API URL (default: https://api.snipara.com)
    SNIPARA_IGNORE_OAUTH: Set to "true" to skip OAuth and use API key instead
"""

import asyncio
import os
import sys
import time
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# Configuration
API_URL = os.environ.get("SNIPARA_API_URL", "https://api.snipara.com")

# Auth state (loaded on startup)
_auth_token: str | None = None
_auth_type: str = "none"  # "oauth", "api_key", or "none"
_project_id: str | None = None


def _load_auth() -> tuple[str | None, str, str | None]:
    """
    Load authentication credentials in priority order:
    1. OAuth token from ~/.snipara/tokens.json (unless SNIPARA_IGNORE_OAUTH=true)
    2. API key from environment

    Returns:
        Tuple of (token, auth_type, project_id)
    """
    # Check if OAuth should be skipped
    ignore_oauth = os.environ.get("SNIPARA_IGNORE_OAUTH", "").lower() in ("true", "1", "yes")

    # Try OAuth tokens first (unless ignored)
    if not ignore_oauth:
        try:
            from .auth import load_tokens
            tokens = load_tokens()
            if tokens:
                # If PROJECT_ID is set, use that project's token
                env_project_id = os.environ.get("SNIPARA_PROJECT_ID")
                if env_project_id and env_project_id in tokens:
                    token_data = tokens[env_project_id]
                    access_token = token_data.get("access_token")
                    if access_token:
                        return access_token, "oauth", env_project_id
                # Otherwise, use the first available token
                for project_id, token_data in tokens.items():
                    access_token = token_data.get("access_token")
                    if access_token:
                        return access_token, "oauth", project_id
        except ImportError:
            pass  # auth module not available
        except Exception:
            pass  # Token loading failed

    # Fall back to API key
    api_key = os.environ.get("SNIPARA_API_KEY", "")
    project_id = os.environ.get("SNIPARA_PROJECT_ID", "")
    if api_key and project_id:
        return api_key, "api_key", project_id

    return None, "none", project_id or None


# Load auth on module import
_auth_token, _auth_type, _project_id = _load_auth()

# Legacy compatibility
API_KEY = _auth_token or os.environ.get("SNIPARA_API_KEY", "")
PROJECT_ID = _project_id or os.environ.get("SNIPARA_PROJECT_ID", "")

# Session context cache
_session_context: str = ""

# Settings cache (5 minute TTL)
_settings_cache: dict[str, Any] = {}
_settings_cache_time: float = 0
SETTINGS_CACHE_TTL = 300  # 5 minutes


async def get_project_settings() -> dict[str, Any]:
    """Fetch project automation settings from API with caching."""
    global _settings_cache, _settings_cache_time

    # Return cached settings if still valid
    if _settings_cache and (time.time() - _settings_cache_time) < SETTINGS_CACHE_TTL:
        return _settings_cache

    # Fetch fresh settings from API
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{API_URL}/v1/{PROJECT_ID}/automation",
                headers=get_headers(),
            )
            if response.status_code == 200:
                data = response.json()
                _settings_cache = data.get("settings", {})
                _settings_cache_time = time.time()
                return _settings_cache
    except Exception:
        pass  # Fall back to defaults on error

    # Return defaults if API fails
    return {
        "maxTokensPerQuery": 4000,
        "searchMode": "hybrid",
        "includeSummaries": True,
        "autoInjectContext": False,
        "enrichPrompts": False,
    }

server = Server("snipara")


def get_headers() -> dict[str, str]:
    """Get request headers with appropriate auth."""
    headers = {"Content-Type": "application/json"}

    if _auth_type == "oauth" and _auth_token:
        headers["Authorization"] = f"Bearer {_auth_token}"
    elif _auth_type == "api_key" and _auth_token:
        headers["X-API-Key"] = _auth_token
    elif API_KEY:
        # Legacy fallback
        headers["X-API-Key"] = API_KEY

    return headers


async def call_api(tool: str, params: dict[str, Any]) -> dict[str, Any]:
    """Call the Snipara MCP API."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{API_URL}/v1/{PROJECT_ID}/mcp",
            headers=get_headers(),
            json={"tool": tool, "params": params},
        )
        response.raise_for_status()
        return response.json()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available Snipara tools."""
    return [
        Tool(
            name="rlm_context_query",
            description="""Query optimized context from your documentation.

Returns ranked, relevant sections that fit within your token budget.
This is the PRIMARY tool - use it for any documentation questions.

Examples:
- "How does authentication work?"
- "What are the API endpoints?"
- "Where is the database schema?"

Returns sections with relevance scores, file paths, and line numbers.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Your question"},
                    "max_tokens": {"type": "integer", "default": 4000, "description": "Token budget"},
                    "search_mode": {"type": "string", "enum": ["keyword", "semantic", "hybrid"], "default": "hybrid"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="rlm_ask",
            description="Query documentation (basic). Use rlm_context_query for better results.",
            inputSchema={
                "type": "object",
                "properties": {"question": {"type": "string", "description": "The question to ask"}},
                "required": ["question"],
            },
        ),
        Tool(
            name="rlm_search",
            description="Search documentation for a pattern (regex supported).",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {"type": "string", "description": "Regex pattern"},
                    "max_results": {"type": "integer", "default": 20},
                },
                "required": ["pattern"],
            },
        ),
        Tool(
            name="rlm_decompose",
            description="Break complex query into sub-queries with execution order.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Complex question to decompose"},
                    "max_depth": {"type": "integer", "default": 2},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="rlm_multi_query",
            description="Execute multiple queries in one call with shared token budget.",
            inputSchema={
                "type": "object",
                "properties": {
                    "queries": {
                        "type": "array",
                        "items": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
                    },
                    "max_tokens": {"type": "integer", "default": 8000},
                },
                "required": ["queries"],
            },
        ),
        Tool(
            name="rlm_inject",
            description="Set session context for subsequent queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {"type": "string", "description": "Context to inject"},
                    "append": {"type": "boolean", "default": False},
                },
                "required": ["context"],
            },
        ),
        Tool(
            name="rlm_context",
            description="Show current session context.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="rlm_clear_context",
            description="Clear session context.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="rlm_stats",
            description="Show documentation statistics.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="rlm_sections",
            description="List all document sections.",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="rlm_read",
            description="Read specific lines from documentation.",
            inputSchema={
                "type": "object",
                "properties": {"start_line": {"type": "integer"}, "end_line": {"type": "integer"}},
                "required": ["start_line", "end_line"],
            },
        ),
        Tool(
            name="rlm_settings",
            description="Show current project settings from dashboard (max_tokens, search_mode, etc.).",
            inputSchema={"type": "object", "properties": {"refresh": {"type": "boolean", "default": False, "description": "Force refresh from API"}}, "required": []},
        ),
        Tool(
            name="rlm_upload_document",
            description="Upload or update a document in the project. Supports .md, .txt, .mdx files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Document path (e.g., 'docs/api.md')"},
                    "content": {"type": "string", "description": "Document content (markdown)"},
                },
                "required": ["path", "content"],
            },
        ),
        Tool(
            name="rlm_sync_documents",
            description="Bulk sync multiple documents. Use for batch uploads or CI/CD integration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "documents": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"},
                                "content": {"type": "string"},
                            },
                            "required": ["path", "content"],
                        },
                        "description": "Documents to sync",
                    },
                    "delete_missing": {"type": "boolean", "default": False, "description": "Delete docs not in list"},
                },
                "required": ["documents"],
            },
        ),
        # Phase 4.5: Planning
        Tool(
            name="rlm_plan",
            description="Generate execution plan for complex queries. Returns step-by-step plan with dependencies.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Complex question to plan for"},
                    "strategy": {
                        "type": "string",
                        "enum": ["breadth_first", "depth_first", "relevance_first"],
                        "default": "relevance_first",
                        "description": "Execution strategy",
                    },
                    "max_tokens": {"type": "integer", "default": 16000, "description": "Total token budget"},
                },
                "required": ["query"],
            },
        ),
        # Phase 4.6: Summary Storage
        Tool(
            name="rlm_store_summary",
            description="Store LLM-generated summary for a document. Enables faster future queries.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_path": {"type": "string", "description": "Path to the document"},
                    "summary": {"type": "string", "description": "Summary text to store"},
                    "summary_type": {
                        "type": "string",
                        "enum": ["concise", "detailed", "technical", "keywords", "custom"],
                        "default": "concise",
                        "description": "Type of summary",
                    },
                    "section_id": {"type": "string", "description": "Optional section identifier"},
                    "line_start": {"type": "integer", "description": "Optional start line"},
                    "line_end": {"type": "integer", "description": "Optional end line"},
                    "generated_by": {"type": "string", "description": "Model that generated the summary"},
                },
                "required": ["document_path", "summary"],
            },
        ),
        Tool(
            name="rlm_get_summaries",
            description="Retrieve stored summaries with optional filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "document_path": {"type": "string", "description": "Filter by document path"},
                    "summary_type": {
                        "type": "string",
                        "enum": ["concise", "detailed", "technical", "keywords", "custom"],
                        "description": "Filter by summary type",
                    },
                    "section_id": {"type": "string", "description": "Filter by section ID"},
                    "include_content": {"type": "boolean", "default": True, "description": "Include summary content"},
                },
                "required": [],
            },
        ),
        Tool(
            name="rlm_delete_summary",
            description="Delete stored summaries by ID, document path, or type.",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary_id": {"type": "string", "description": "Specific summary ID to delete"},
                    "document_path": {"type": "string", "description": "Delete all summaries for document"},
                    "summary_type": {
                        "type": "string",
                        "enum": ["concise", "detailed", "technical", "keywords", "custom"],
                        "description": "Delete summaries of this type",
                    },
                },
                "required": [],
            },
        ),
        # Phase 7: Shared Context
        Tool(
            name="rlm_shared_context",
            description="Get merged context from linked shared collections. Returns categorized docs with budget allocation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_tokens": {"type": "integer", "default": 4000, "description": "Token budget"},
                    "categories": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["MANDATORY", "BEST_PRACTICES", "GUIDELINES", "REFERENCE"],
                        },
                        "description": "Filter by categories (default: all)",
                    },
                    "include_content": {"type": "boolean", "default": True, "description": "Include merged content"},
                },
                "required": [],
            },
        ),
        Tool(
            name="rlm_list_templates",
            description="List available prompt templates from shared collections.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {"type": "string", "description": "Filter by category"},
                },
                "required": [],
            },
        ),
        Tool(
            name="rlm_get_template",
            description="Get a specific prompt template by ID or slug. Optionally render with variables.",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {"type": "string", "description": "Template ID"},
                    "slug": {"type": "string", "description": "Template slug"},
                    "variables": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "Variables to substitute in template",
                    },
                },
                "required": [],
            },
        ),
        # Phase 8.2: Agent Memory Tools
        Tool(
            name="rlm_remember",
            description="""Store a memory for later semantic recall.

Memories can be facts, decisions, learnings, preferences, todos, or context.
Each memory gets a confidence score that decays over time if not accessed.

Examples:
- Remember a user preference: type="preference", content="User prefers dark mode"
- Store a learned fact: type="fact", content="API uses JWT for auth"
- Record a decision: type="decision", content="Chose React over Vue for frontend"
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The memory content to store"},
                    "type": {
                        "type": "string",
                        "enum": ["fact", "decision", "learning", "preference", "todo", "context"],
                        "default": "fact",
                        "description": "Type of memory",
                    },
                    "scope": {
                        "type": "string",
                        "enum": ["agent", "project", "team", "user"],
                        "default": "project",
                        "description": "Visibility scope",
                    },
                    "category": {"type": "string", "description": "Optional category for grouping"},
                    "ttl_days": {"type": "integer", "description": "Days until expiration (null = permanent)"},
                    "related_to": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "IDs of related memories",
                    },
                    "document_refs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Referenced document paths",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="rlm_recall",
            description="""Semantically recall relevant memories based on a query.

Uses embeddings to find memories similar to the query, weighted by confidence.
Confidence decays over time if memories aren't accessed.

Examples:
- "What did the user say about their preferences?"
- "What decisions did we make about the architecture?"
- "What did I learn about the authentication system?"
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "type": {
                        "type": "string",
                        "enum": ["fact", "decision", "learning", "preference", "todo", "context"],
                        "description": "Filter by memory type",
                    },
                    "scope": {
                        "type": "string",
                        "enum": ["agent", "project", "team", "user"],
                        "description": "Filter by scope",
                    },
                    "category": {"type": "string", "description": "Filter by category"},
                    "limit": {"type": "integer", "default": 5, "description": "Maximum memories to return"},
                    "min_relevance": {"type": "number", "default": 0.5, "description": "Minimum relevance score (0-1)"},
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="rlm_memories",
            description="List memories with optional filters. For browsing stored memories without semantic search.",
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["fact", "decision", "learning", "preference", "todo", "context"],
                        "description": "Filter by memory type",
                    },
                    "scope": {
                        "type": "string",
                        "enum": ["agent", "project", "team", "user"],
                        "description": "Filter by scope",
                    },
                    "category": {"type": "string", "description": "Filter by category"},
                    "search": {"type": "string", "description": "Text search in content"},
                    "limit": {"type": "integer", "default": 20, "description": "Maximum memories to return"},
                    "offset": {"type": "integer", "default": 0, "description": "Pagination offset"},
                },
                "required": [],
            },
        ),
        Tool(
            name="rlm_forget",
            description="Delete memories by ID or filter criteria. Use with caution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {"type": "string", "description": "Specific memory ID to delete"},
                    "type": {
                        "type": "string",
                        "enum": ["fact", "decision", "learning", "preference", "todo", "context"],
                        "description": "Delete all of this type",
                    },
                    "category": {"type": "string", "description": "Delete all in this category"},
                    "older_than_days": {"type": "integer", "description": "Delete memories older than N days"},
                },
                "required": [],
            },
        ),
        # Phase 9.1: Multi-Agent Swarm Tools
        Tool(
            name="rlm_swarm_create",
            description="""Create a new agent swarm for multi-agent coordination.

Swarms allow multiple agents to work together with shared state, resource claims, and task queues.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Swarm name"},
                    "description": {"type": "string", "description": "Swarm description"},
                    "max_agents": {"type": "integer", "default": 10, "description": "Maximum agents allowed"},
                    "config": {"type": "object", "description": "Optional swarm configuration"},
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="rlm_swarm_join",
            description="Join an existing swarm as an agent.",
            inputSchema={
                "type": "object",
                "properties": {
                    "swarm_id": {"type": "string", "description": "Swarm to join"},
                    "agent_id": {"type": "string", "description": "Your unique agent identifier"},
                    "role": {
                        "type": "string",
                        "enum": ["coordinator", "worker", "observer"],
                        "default": "worker",
                        "description": "Your role in the swarm",
                    },
                    "capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Your capabilities (e.g., 'code', 'test', 'review')",
                    },
                },
                "required": ["swarm_id", "agent_id"],
            },
        ),
        Tool(
            name="rlm_claim",
            description="""Claim exclusive access to a resource (file, function, module).

Claims prevent other agents from modifying the same resource simultaneously.
Claims auto-expire after timeout to prevent deadlocks.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "swarm_id": {"type": "string", "description": "Swarm ID"},
                    "agent_id": {"type": "string", "description": "Your agent identifier"},
                    "resource_type": {
                        "type": "string",
                        "enum": ["file", "function", "module", "component", "other"],
                        "description": "Type of resource",
                    },
                    "resource_id": {"type": "string", "description": "Resource identifier (e.g., file path)"},
                    "timeout_seconds": {"type": "integer", "default": 300, "description": "Claim timeout"},
                },
                "required": ["swarm_id", "agent_id", "resource_type", "resource_id"],
            },
        ),
        Tool(
            name="rlm_release",
            description="Release a claimed resource.",
            inputSchema={
                "type": "object",
                "properties": {
                    "swarm_id": {"type": "string", "description": "Swarm ID"},
                    "agent_id": {"type": "string", "description": "Your agent identifier"},
                    "claim_id": {"type": "string", "description": "Claim ID to release"},
                    "resource_type": {"type": "string", "description": "Resource type (alternative to claim_id)"},
                    "resource_id": {"type": "string", "description": "Resource ID (alternative to claim_id)"},
                },
                "required": ["swarm_id", "agent_id"],
            },
        ),
        Tool(
            name="rlm_state_get",
            description="Read shared swarm state by key.",
            inputSchema={
                "type": "object",
                "properties": {
                    "swarm_id": {"type": "string", "description": "Swarm ID"},
                    "key": {"type": "string", "description": "State key to read"},
                },
                "required": ["swarm_id", "key"],
            },
        ),
        Tool(
            name="rlm_state_set",
            description="""Write shared swarm state with optimistic locking.

Provide expected_version to prevent lost updates from concurrent modifications.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "swarm_id": {"type": "string", "description": "Swarm ID"},
                    "agent_id": {"type": "string", "description": "Your agent identifier"},
                    "key": {"type": "string", "description": "State key"},
                    "value": {"description": "Value to set (any JSON-serializable type)"},
                    "expected_version": {"type": "integer", "description": "Expected version for optimistic locking"},
                },
                "required": ["swarm_id", "agent_id", "key", "value"],
            },
        ),
        Tool(
            name="rlm_broadcast",
            description="Send an event to all agents in the swarm.",
            inputSchema={
                "type": "object",
                "properties": {
                    "swarm_id": {"type": "string", "description": "Swarm ID"},
                    "agent_id": {"type": "string", "description": "Your agent identifier"},
                    "event_type": {"type": "string", "description": "Event type (e.g., 'task_completed', 'error')"},
                    "payload": {"type": "object", "description": "Event data"},
                },
                "required": ["swarm_id", "agent_id", "event_type"],
            },
        ),
        Tool(
            name="rlm_task_create",
            description="Create a task in the swarm's distributed task queue.",
            inputSchema={
                "type": "object",
                "properties": {
                    "swarm_id": {"type": "string", "description": "Swarm ID"},
                    "agent_id": {"type": "string", "description": "Creating agent identifier"},
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"},
                    "priority": {"type": "integer", "default": 0, "description": "Priority (higher = more urgent)"},
                    "depends_on": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Task IDs this depends on",
                    },
                    "metadata": {"type": "object", "description": "Additional task data"},
                },
                "required": ["swarm_id", "agent_id", "title"],
            },
        ),
        Tool(
            name="rlm_task_claim",
            description="""Claim a task from the queue.

If task_id not specified, claims the highest priority task with all dependencies satisfied.
""",
            inputSchema={
                "type": "object",
                "properties": {
                    "swarm_id": {"type": "string", "description": "Swarm ID"},
                    "agent_id": {"type": "string", "description": "Your agent identifier"},
                    "task_id": {"type": "string", "description": "Specific task to claim (optional)"},
                    "timeout_seconds": {"type": "integer", "default": 600, "description": "Task timeout"},
                },
                "required": ["swarm_id", "agent_id"],
            },
        ),
        Tool(
            name="rlm_task_complete",
            description="Mark a claimed task as completed or failed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "swarm_id": {"type": "string", "description": "Swarm ID"},
                    "agent_id": {"type": "string", "description": "Your agent identifier"},
                    "task_id": {"type": "string", "description": "Task to complete"},
                    "success": {"type": "boolean", "default": True, "description": "Whether task succeeded"},
                    "result": {"description": "Task result data"},
                },
                "required": ["swarm_id", "agent_id", "task_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    global _session_context

    try:
        if name == "rlm_context_query":
            # Get project settings from dashboard (cached)
            settings = await get_project_settings()

            query = arguments["query"]
            if _session_context:
                query = f"Context: {_session_context}\n\nQuestion: {query}"

            # Use settings from dashboard, allow override from arguments
            max_tokens = arguments.get("max_tokens") or settings.get("maxTokensPerQuery", 4000)
            search_mode = arguments.get("search_mode") or settings.get("searchMode", "hybrid")
            include_summaries = settings.get("includeSummaries", True)

            result = await call_api("rlm_context_query", {
                "query": query,
                "max_tokens": max_tokens,
                "search_mode": search_mode,
                "include_metadata": True,
                "prefer_summaries": include_summaries,
            })

            if result.get("success"):
                data = result.get("result", {})
                sections = data.get("sections", [])
                if sections:
                    parts = []
                    # Prepend system instructions if provided
                    if data.get("system_instructions"):
                        parts.append(data["system_instructions"])
                    parts.append("## Relevant Documentation\n")
                    for s in sections:
                        parts.append(f"### {s.get('title', 'Untitled')}")
                        parts.append(f"*{s.get('file', '')} | Score: {s.get('relevance_score', 0):.2f}*\n")
                        parts.append(s.get("content", ""))
                        parts.append("")
                    parts.append(f"---\n*{len(sections)} sections, {data.get('total_tokens', 0)} tokens*")
                    return [TextContent(type="text", text="\n".join(parts))]
                return [TextContent(type="text", text="No relevant documentation found.")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_ask":
            question = arguments["question"]
            if _session_context:
                question = f"Context: {_session_context}\n\nQuestion: {question}"

            result = await call_api("rlm_context_query", {
                "query": question, "max_tokens": 4000, "search_mode": "hybrid", "include_metadata": True,
            })

            if result.get("success"):
                data = result.get("result", {})
                sections = data.get("sections", [])
                if sections:
                    parts = ["## Relevant Documentation\n"]
                    for s in sections:
                        parts.append(f"### {s.get('title', 'Untitled')}")
                        parts.append(f"*{s.get('file', '')}*\n")
                        parts.append(s.get("content", ""))
                        parts.append("")
                    return [TextContent(type="text", text="\n".join(parts))]
                return [TextContent(type="text", text="No relevant documentation found.")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_search":
            result = await call_api("rlm_search", {"pattern": arguments["pattern"]})
            if result.get("success"):
                matches = result.get("result", {}).get("matches", [])
                max_results = arguments.get("max_results", 20)
                if matches:
                    lines = [f"Found {len(matches)} matches:\n"]
                    for m in matches[:max_results]:
                        lines.append(f"  {m.get('file', '')}:{m.get('line_number', 0)}: {m.get('content', '')[:100]}")
                    if len(matches) > max_results:
                        lines.append(f"\n... and {len(matches) - max_results} more")
                    return [TextContent(type="text", text="\n".join(lines))]
                return [TextContent(type="text", text=f"No matches for '{arguments['pattern']}'")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_decompose":
            result = await call_api("rlm_decompose", {"query": arguments["query"], "max_depth": arguments.get("max_depth", 2)})
            if result.get("success"):
                data = result.get("result", {})
                sub = data.get("sub_queries", [])
                lines = [f"**Decomposed into {len(sub)} sub-queries:**\n"]
                for q in sub:
                    lines.append(f"{q.get('id', 0)}. {q.get('query', '')} (priority: {q.get('priority', 1)})")
                lines.append(f"\n**Suggested order:** {data.get('suggested_sequence', [])}")
                return [TextContent(type="text", text="\n".join(lines))]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_multi_query":
            result = await call_api("rlm_multi_query", {
                "queries": arguments["queries"], "max_tokens": arguments.get("max_tokens", 8000),
            })
            if result.get("success"):
                data = result.get("result", {})
                parts = [f"**Executed {data.get('queries_executed', 0)} queries:**\n"]
                for r in data.get("results", []):
                    parts.append(f"### {r.get('query', '')}")
                    for s in r.get("sections", [])[:2]:
                        parts.append(f"- {s.get('title', '')} ({s.get('file', '')})")
                    parts.append("")
                parts.append(f"*Total: {data.get('total_tokens', 0)} tokens*")
                return [TextContent(type="text", text="\n".join(parts))]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_inject":
            ctx = arguments["context"]
            if arguments.get("append") and _session_context:
                _session_context = _session_context + "\n\n" + ctx
            else:
                _session_context = ctx
            try:
                await call_api("rlm_inject", {"context": _session_context})
            except Exception:
                pass
            return [TextContent(type="text", text=f"Session context {'appended' if arguments.get('append') else 'set'} ({len(_session_context)} chars)")]

        elif name == "rlm_context":
            if _session_context:
                return [TextContent(type="text", text=f"**Session Context:**\n\n{_session_context}")]
            return [TextContent(type="text", text="No session context. Use rlm_inject to set.")]

        elif name == "rlm_clear_context":
            if _session_context:
                _session_context = ""
                try:
                    await call_api("rlm_clear_context", {})
                except Exception:
                    pass
                return [TextContent(type="text", text="Session context cleared.")]
            return [TextContent(type="text", text="No context to clear.")]

        elif name == "rlm_stats":
            result = await call_api("rlm_stats", {})
            if result.get("success"):
                # Handle both "result" and "data" keys from different API responses
                d = result.get("result", result.get("data", {}))
                # Backend returns total_characters, not total_tokens
                files_loaded = d.get('files_loaded', d.get('document_count', 0))
                total_lines = d.get('total_lines', 0)
                total_chars = d.get('total_characters', 0)
                sections = d.get('sections', d.get('chunk_count', 0))
                # Safe formatting - convert to int if numeric string, else show as-is
                def fmt(v):
                    if isinstance(v, (int, float)):
                        return f"{int(v):,}"
                    if isinstance(v, str) and v.isdigit():
                        return f"{int(v):,}"
                    return str(v) if v else "0"
                return [TextContent(type="text", text=f"**Stats:**\n- Files: {fmt(files_loaded)}\n- Lines: {fmt(total_lines)}\n- Characters: {fmt(total_chars)}\n- Sections: {fmt(sections)}")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_sections":
            result = await call_api("rlm_sections", {})
            if result.get("success"):
                sections = result.get("result", {}).get("sections", [])
                lines = ["**Documents:**\n"]
                for s in sections:
                    lines.append(f"- {s.get('path', '')} ({s.get('chunk_count', 0)} chunks)")
                return [TextContent(type="text", text="\n".join(lines))]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_read":
            result = await call_api("rlm_read", {"start_line": arguments["start_line"], "end_line": arguments["end_line"]})
            if result.get("success"):
                content = result.get("result", {}).get("content", "")
                return [TextContent(type="text", text=f"**Lines {arguments['start_line']}-{arguments['end_line']}:**\n```\n{content}\n```")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_settings":
            global _settings_cache, _settings_cache_time
            # Force refresh if requested
            if arguments.get("refresh"):
                _settings_cache = {}
                _settings_cache_time = 0
            settings = await get_project_settings()
            cache_age = int(time.time() - _settings_cache_time) if _settings_cache_time else 0
            lines = [
                "**Project Settings** (from dashboard)\n",
                f"- Max Tokens: {settings.get('maxTokensPerQuery', 4000)}",
                f"- Search Mode: {settings.get('searchMode', 'hybrid')}",
                f"- Include Summaries: {settings.get('includeSummaries', True)}",
                f"- Auto-Inject Context: {settings.get('autoInjectContext', False)}",
                f"- Enrich Prompts: {settings.get('enrichPrompts', False)}",
                f"\n*Cache age: {cache_age}s (TTL: {SETTINGS_CACHE_TTL}s)*",
            ]
            return [TextContent(type="text", text="\n".join(lines))]

        elif name == "rlm_upload_document":
            result = await call_api("rlm_upload_document", {
                "path": arguments["path"],
                "content": arguments["content"],
            })
            if result.get("success"):
                data = result.get("result", {})
                return [TextContent(type="text", text=f"**Document {data.get('action', 'processed')}:** {data.get('path', '')} ({data.get('size', 0)} bytes)")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_sync_documents":
            result = await call_api("rlm_sync_documents", {
                "documents": arguments["documents"],
                "delete_missing": arguments.get("delete_missing", False),
            })
            if result.get("success"):
                data = result.get("result", {})
                return [TextContent(type="text", text=f"**Sync complete:** {data.get('created', 0)} created, {data.get('updated', 0)} updated, {data.get('unchanged', 0)} unchanged, {data.get('deleted', 0)} deleted")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        # Phase 4.5: Planning
        elif name == "rlm_plan":
            result = await call_api("rlm_plan", {
                "query": arguments["query"],
                "strategy": arguments.get("strategy", "relevance_first"),
                "max_tokens": arguments.get("max_tokens", 16000),
            })
            if result.get("success"):
                data = result.get("result", {})
                steps = data.get("steps", [])
                lines = [
                    f"**Execution Plan** ({data.get('plan_id', 'unknown')})\n",
                    f"Strategy: {data.get('strategy', 'relevance_first')}",
                    f"Estimated tokens: {data.get('estimated_total_tokens', 0)}\n",
                    "**Steps:**",
                ]
                for step in steps:
                    deps = f" (depends on: {step.get('depends_on', [])})" if step.get("depends_on") else ""
                    lines.append(f"{step.get('step', 0)}. {step.get('action', '')} → {step.get('expected_output', '')}{deps}")
                return [TextContent(type="text", text="\n".join(lines))]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        # Phase 4.6: Summary Storage
        elif name == "rlm_store_summary":
            result = await call_api("rlm_store_summary", {
                "document_path": arguments["document_path"],
                "summary": arguments["summary"],
                "summary_type": arguments.get("summary_type", "concise"),
                "section_id": arguments.get("section_id"),
                "line_start": arguments.get("line_start"),
                "line_end": arguments.get("line_end"),
                "generated_by": arguments.get("generated_by"),
            })
            if result.get("success"):
                data = result.get("result", {})
                action = "created" if data.get("created") else "updated"
                return [TextContent(type="text", text=f"**Summary {action}:** {data.get('document_path', '')} ({data.get('summary_type', '')})\nTokens: {data.get('token_count', 0)} | ID: {data.get('summary_id', '')}")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_get_summaries":
            result = await call_api("rlm_get_summaries", {
                "document_path": arguments.get("document_path"),
                "summary_type": arguments.get("summary_type"),
                "section_id": arguments.get("section_id"),
                "include_content": arguments.get("include_content", True),
            })
            if result.get("success"):
                data = result.get("result", {})
                summaries = data.get("summaries", [])
                if summaries:
                    lines = [f"**Found {len(summaries)} summaries** ({data.get('total_tokens', 0)} tokens)\n"]
                    for s in summaries:
                        lines.append(f"- **{s.get('document_path', '')}** ({s.get('summary_type', '')})")
                        if s.get("content"):
                            preview = s["content"][:200] + "..." if len(s.get("content", "")) > 200 else s.get("content", "")
                            lines.append(f"  {preview}")
                    return [TextContent(type="text", text="\n".join(lines))]
                return [TextContent(type="text", text="No summaries found.")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_delete_summary":
            result = await call_api("rlm_delete_summary", {
                "summary_id": arguments.get("summary_id"),
                "document_path": arguments.get("document_path"),
                "summary_type": arguments.get("summary_type"),
            })
            if result.get("success"):
                data = result.get("result", {})
                return [TextContent(type="text", text=f"**Deleted:** {data.get('deleted_count', 0)} summary(ies)")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        # Phase 7: Shared Context
        elif name == "rlm_shared_context":
            result = await call_api("rlm_shared_context", {
                "max_tokens": arguments.get("max_tokens", 4000),
                "categories": arguments.get("categories"),
                "include_content": arguments.get("include_content", True),
            })
            if result.get("success"):
                data = result.get("result", {})
                docs = data.get("documents", [])
                if docs:
                    lines = [
                        f"**Shared Context** ({data.get('collections_loaded', 0)} collections)\n",
                        f"Total tokens: {data.get('total_tokens', 0)} | Hash: {data.get('context_hash', '')[:8]}...\n",
                    ]
                    # Group by category
                    by_cat: dict[str, list] = {}
                    for d in docs:
                        cat = d.get("category", "OTHER")
                        if cat not in by_cat:
                            by_cat[cat] = []
                        by_cat[cat].append(d)
                    for cat in ["MANDATORY", "BEST_PRACTICES", "GUIDELINES", "REFERENCE"]:
                        if cat in by_cat:
                            lines.append(f"**{cat}:**")
                            for d in by_cat[cat]:
                                lines.append(f"  - {d.get('title', 'Untitled')} ({d.get('token_count', 0)} tokens)")
                    if data.get("merged_content"):
                        lines.append("\n---\n")
                        lines.append(data["merged_content"])
                    return [TextContent(type="text", text="\n".join(lines))]
                return [TextContent(type="text", text="No shared context linked to this project.")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_list_templates":
            result = await call_api("rlm_list_templates", {
                "category": arguments.get("category"),
            })
            if result.get("success"):
                data = result.get("result", {})
                templates = data.get("templates", [])
                if templates:
                    lines = [f"**Available Templates** ({len(templates)} total)\n"]
                    # Group by category
                    by_cat: dict[str, list] = {}
                    for t in templates:
                        cat = t.get("category", "general")
                        if cat not in by_cat:
                            by_cat[cat] = []
                        by_cat[cat].append(t)
                    for cat, temps in by_cat.items():
                        lines.append(f"**{cat}:**")
                        for t in temps:
                            desc = f" - {t['description']}" if t.get("description") else ""
                            vars_str = f" (vars: {', '.join(t.get('variables', []))})" if t.get("variables") else ""
                            lines.append(f"  - `{t.get('slug', '')}`: {t.get('name', '')}{desc}{vars_str}")
                    return [TextContent(type="text", text="\n".join(lines))]
                return [TextContent(type="text", text="No templates found.")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_get_template":
            result = await call_api("rlm_get_template", {
                "template_id": arguments.get("template_id"),
                "slug": arguments.get("slug"),
                "variables": arguments.get("variables", {}),
            })
            if result.get("success"):
                data = result.get("result", {})
                template = data.get("template")
                if template:
                    lines = [
                        f"**{template.get('name', 'Template')}** (`{template.get('slug', '')}`)\n",
                        f"Category: {template.get('category', '')} | Collection: {template.get('collection_name', '')}",
                    ]
                    if template.get("description"):
                        lines.append(f"Description: {template['description']}")
                    if template.get("variables"):
                        lines.append(f"Variables: {', '.join(template['variables'])}")
                    missing = data.get("missing_variables", [])
                    if missing:
                        lines.append(f"\n⚠️ Missing variables: {', '.join(missing)}")
                    lines.append("\n**Rendered Prompt:**\n```")
                    lines.append(data.get("rendered_prompt", template.get("prompt", "")))
                    lines.append("```")
                    return [TextContent(type="text", text="\n".join(lines))]
                return [TextContent(type="text", text="Template not found.")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        # Phase 8.2: Agent Memory Handlers
        elif name == "rlm_remember":
            result = await call_api("rlm_remember", {
                "content": arguments["content"],
                "type": arguments.get("type", "fact"),
                "scope": arguments.get("scope", "project"),
                "category": arguments.get("category"),
                "ttl_days": arguments.get("ttl_days"),
                "related_to": arguments.get("related_to"),
                "document_refs": arguments.get("document_refs"),
            })
            if result.get("success"):
                data = result.get("result", {})
                return [TextContent(type="text", text=f"**Memory stored** (ID: {data.get('memory_id', '')})\nType: {data.get('type', '')} | Scope: {data.get('scope', '')}")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_recall":
            result = await call_api("rlm_recall", {
                "query": arguments["query"],
                "type": arguments.get("type"),
                "scope": arguments.get("scope"),
                "category": arguments.get("category"),
                "limit": arguments.get("limit", 5),
                "min_relevance": arguments.get("min_relevance", 0.5),
            })
            if result.get("success"):
                data = result.get("result", {})
                memories = data.get("memories", [])
                if memories:
                    lines = [f"**Recalled {len(memories)} memories** (searched {data.get('total_searched', 0)})\n"]
                    for m in memories:
                        conf = m.get("confidence", 1.0)
                        rel = m.get("relevance", 0)
                        lines.append(f"**[{m.get('type', '')}]** {m.get('content', '')[:200]}")
                        lines.append(f"  *Relevance: {rel:.2f} | Confidence: {conf:.2f} | Accessed: {m.get('access_count', 0)}x*\n")
                    return [TextContent(type="text", text="\n".join(lines))]
                return [TextContent(type="text", text="No relevant memories found.")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_memories":
            result = await call_api("rlm_memories", {
                "type": arguments.get("type"),
                "scope": arguments.get("scope"),
                "category": arguments.get("category"),
                "search": arguments.get("search"),
                "limit": arguments.get("limit", 20),
                "offset": arguments.get("offset", 0),
            })
            if result.get("success"):
                data = result.get("result", {})
                memories = data.get("memories", [])
                if memories:
                    lines = [f"**{data.get('total_count', len(memories))} memories** (showing {len(memories)})\n"]
                    for m in memories:
                        lines.append(f"- **[{m.get('type', '')}]** {m.get('content', '')[:100]}...")
                        lines.append(f"  *ID: {m.get('memory_id', '')} | Category: {m.get('category', 'none')}*")
                    if data.get("has_more"):
                        lines.append(f"\n*More results available (offset: {arguments.get('offset', 0) + len(memories)})*")
                    return [TextContent(type="text", text="\n".join(lines))]
                return [TextContent(type="text", text="No memories found.")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_forget":
            result = await call_api("rlm_forget", {
                "memory_id": arguments.get("memory_id"),
                "type": arguments.get("type"),
                "category": arguments.get("category"),
                "older_than_days": arguments.get("older_than_days"),
            })
            if result.get("success"):
                data = result.get("result", {})
                return [TextContent(type="text", text=f"**{data.get('message', 'Deleted')}** ({data.get('deleted_count', 0)} memories)")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        # Phase 9.1: Multi-Agent Swarm Handlers
        elif name == "rlm_swarm_create":
            result = await call_api("rlm_swarm_create", {
                "name": arguments["name"],
                "description": arguments.get("description"),
                "max_agents": arguments.get("max_agents", 10),
                "config": arguments.get("config"),
            })
            if result.get("success"):
                data = result.get("result", {})
                return [TextContent(type="text", text=f"**Swarm created:** {data.get('name', '')}\nID: {data.get('swarm_id', '')} | Max agents: {data.get('max_agents', 10)}")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_swarm_join":
            result = await call_api("rlm_swarm_join", {
                "swarm_id": arguments["swarm_id"],
                "agent_id": arguments["agent_id"],
                "role": arguments.get("role", "worker"),
                "capabilities": arguments.get("capabilities"),
            })
            if result.get("success"):
                data = result.get("result", {})
                return [TextContent(type="text", text=f"**Joined swarm** as {data.get('role', 'worker')}\nAgent ID: {data.get('agent_id', '')}")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_claim":
            result = await call_api("rlm_claim", {
                "swarm_id": arguments["swarm_id"],
                "agent_id": arguments["agent_id"],
                "resource_type": arguments["resource_type"],
                "resource_id": arguments["resource_id"],
                "timeout_seconds": arguments.get("timeout_seconds", 300),
            })
            if result.get("success"):
                data = result.get("result", {})
                if data.get("extended"):
                    return [TextContent(type="text", text=f"**Claim extended** until {data.get('expires_at', '')}")]
                return [TextContent(type="text", text=f"**Resource claimed:** {data.get('resource_type', '')}:{data.get('resource_id', '')}\nExpires: {data.get('expires_at', '')}")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_release":
            result = await call_api("rlm_release", {
                "swarm_id": arguments["swarm_id"],
                "agent_id": arguments["agent_id"],
                "claim_id": arguments.get("claim_id"),
                "resource_type": arguments.get("resource_type"),
                "resource_id": arguments.get("resource_id"),
            })
            if result.get("success"):
                return [TextContent(type="text", text="**Claim released**")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_state_get":
            result = await call_api("rlm_state_get", {
                "swarm_id": arguments["swarm_id"],
                "key": arguments["key"],
            })
            if result.get("success"):
                data = result.get("result", {})
                if data.get("found"):
                    import json as json_mod
                    value_str = json_mod.dumps(data.get("value"), indent=2) if isinstance(data.get("value"), (dict, list)) else str(data.get("value"))
                    return [TextContent(type="text", text=f"**{arguments['key']}** (v{data.get('version', 0)})\n```json\n{value_str}\n```")]
                return [TextContent(type="text", text=f"Key '{arguments['key']}' not found")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_state_set":
            result = await call_api("rlm_state_set", {
                "swarm_id": arguments["swarm_id"],
                "agent_id": arguments["agent_id"],
                "key": arguments["key"],
                "value": arguments["value"],
                "expected_version": arguments.get("expected_version"),
            })
            if result.get("success"):
                data = result.get("result", {})
                return [TextContent(type="text", text=f"**State {data.get('message', 'updated')}:** {arguments['key']} → v{data.get('version', 0)}")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_broadcast":
            result = await call_api("rlm_broadcast", {
                "swarm_id": arguments["swarm_id"],
                "agent_id": arguments["agent_id"],
                "event_type": arguments["event_type"],
                "payload": arguments.get("payload"),
            })
            if result.get("success"):
                data = result.get("result", {})
                redis_status = "✓ real-time" if data.get("redis_published") else "✗ persisted only"
                return [TextContent(type="text", text=f"**Event broadcast:** {arguments['event_type']} ({redis_status})")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_task_create":
            result = await call_api("rlm_task_create", {
                "swarm_id": arguments["swarm_id"],
                "agent_id": arguments["agent_id"],
                "title": arguments["title"],
                "description": arguments.get("description"),
                "priority": arguments.get("priority", 0),
                "depends_on": arguments.get("depends_on"),
                "metadata": arguments.get("metadata"),
            })
            if result.get("success"):
                data = result.get("result", {})
                deps = f" (depends on: {data.get('depends_on', [])})" if data.get("depends_on") else ""
                return [TextContent(type="text", text=f"**Task created:** {arguments['title']}\nID: {data.get('task_id', '')} | Priority: {data.get('priority', 0)}{deps}")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_task_claim":
            result = await call_api("rlm_task_claim", {
                "swarm_id": arguments["swarm_id"],
                "agent_id": arguments["agent_id"],
                "task_id": arguments.get("task_id"),
                "timeout_seconds": arguments.get("timeout_seconds", 600),
            })
            if result.get("success"):
                data = result.get("result", {})
                return [TextContent(type="text", text=f"**Task claimed:** {data.get('title', '')}\nID: {data.get('task_id', '')} | Deadline: {data.get('deadline', '')}")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        elif name == "rlm_task_complete":
            result = await call_api("rlm_task_complete", {
                "swarm_id": arguments["swarm_id"],
                "agent_id": arguments["agent_id"],
                "task_id": arguments["task_id"],
                "success": arguments.get("success", True),
                "result": arguments.get("result"),
            })
            if result.get("success"):
                data = result.get("result", {})
                return [TextContent(type="text", text=f"**Task {data.get('status', 'completed')}:** {arguments['task_id']}")]
            return [TextContent(type="text", text=f"**Error:** {result.get('error', 'Unknown error')}")]

        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except httpx.HTTPStatusError as e:
        return [TextContent(type="text", text=f"**API Error:** {e.response.status_code} - {e.response.text}")]
    except httpx.ConnectError:
        return [TextContent(type="text", text=f"**Connection Error:** Cannot reach {API_URL}")]
    except Exception as e:
        return [TextContent(type="text", text=f"**Error:** {type(e).__name__}: {str(e)}")]


async def run_server():
    """Run the MCP server."""
    global _auth_token, _auth_type, _project_id, API_KEY, PROJECT_ID

    # Reload auth in case it changed
    _auth_token, _auth_type, _project_id = _load_auth()
    API_KEY = _auth_token or os.environ.get("SNIPARA_API_KEY", "")
    PROJECT_ID = _project_id or os.environ.get("SNIPARA_PROJECT_ID", "")

    if not _auth_token and not API_KEY:
        print("Error: No authentication found.", file=sys.stderr)
        print("", file=sys.stderr)
        print("Options:", file=sys.stderr)
        print("  1. Run 'snipara-mcp-login' to authenticate via browser (recommended)", file=sys.stderr)
        print("  2. Set SNIPARA_API_KEY environment variable", file=sys.stderr)
        sys.exit(1)

    if not PROJECT_ID:
        print("Error: No project ID found.", file=sys.stderr)
        if _auth_type == "oauth":
            print("Your OAuth token should include a project ID. Try logging in again.", file=sys.stderr)
        else:
            print("Set SNIPARA_PROJECT_ID environment variable.", file=sys.stderr)
        sys.exit(1)

    # Log auth method for debugging
    if _auth_type == "oauth":
        print(f"Authenticated via OAuth (project: {PROJECT_ID})", file=sys.stderr)
    else:
        print(f"Authenticated via API key (project: {PROJECT_ID})", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    """Entry point for snipara-mcp command."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
