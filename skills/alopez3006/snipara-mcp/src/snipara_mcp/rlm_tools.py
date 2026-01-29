"""
RLM Runtime tool plugins for Snipara context optimization.

This module provides Snipara tools in a format compatible with rlm-runtime.
When snipara-mcp is installed alongside rlm-runtime, these tools are
automatically registered.

Usage:
    # Automatic (in rlm-runtime)
    rlm = RLM(snipara_api_key="...", snipara_project_slug="...")
    # Tools are auto-registered

    # Manual
    from snipara_mcp.rlm_tools import get_snipara_tools
    tools = get_snipara_tools(api_key="...", project_slug="...")
"""

from __future__ import annotations

import os
from typing import Any, TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from rlm.backends.base import Tool

# Default API URL - matches the MCP endpoint format
DEFAULT_API_URL = "https://snipara.com"


class SniparaClient:
    """HTTP client for Snipara MCP API."""

    def __init__(
        self,
        api_key: str,
        project_slug: str,
        api_url: str | None = None,
    ):
        """Initialize the Snipara client.

        Args:
            api_key: Snipara API key (starts with 'rlm_')
            project_slug: Project identifier
            api_url: Optional custom API URL (e.g., https://snipara.com)
        """
        self.api_key = api_key
        self.project_slug = project_slug
        self.api_url = api_url or os.environ.get("SNIPARA_API_URL", DEFAULT_API_URL)
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    async def call_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call a Snipara MCP tool.

        Args:
            tool_name: Name of the tool to call
            params: Tool parameters

        Returns:
            Tool result dictionary
        """
        client = await self._get_client()
        response = await client.post(
            f"{self.api_url}/api/mcp/{self.project_slug}",
            json={"tool": tool_name, "params": params},
        )
        response.raise_for_status()
        result = response.json()

        if not result.get("success"):
            raise RuntimeError(result.get("error", "Unknown error"))

        return result.get("result", {})

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None


def get_snipara_tools(
    api_key: str | None = None,
    project_slug: str | None = None,
    api_url: str | None = None,
) -> list[Tool]:
    """Get Snipara tools as RLM-compatible Tool objects.

    This function is called by rlm-runtime when snipara-mcp is installed
    and Snipara credentials are configured.

    Args:
        api_key: Snipara API key (or SNIPARA_API_KEY env var)
        project_slug: Project slug (or SNIPARA_PROJECT_SLUG env var)
        api_url: Optional custom API URL

    Returns:
        List of Tool objects compatible with rlm-runtime

    Raises:
        ImportError: If rlm-runtime is not installed
        ValueError: If credentials are missing
    """
    # Import Tool from rlm-runtime
    try:
        from rlm.backends.base import Tool
    except ImportError:
        raise ImportError(
            "rlm-runtime is required to use Snipara tools. "
            "Install with: pip install rlm-runtime"
        )

    # Get credentials from args or environment
    api_key = api_key or os.environ.get("SNIPARA_API_KEY")
    project_slug = project_slug or os.environ.get("SNIPARA_PROJECT_SLUG")

    if not api_key:
        raise ValueError(
            "Snipara API key required. Set SNIPARA_API_KEY or pass api_key parameter."
        )
    if not project_slug:
        raise ValueError(
            "Snipara project slug required. Set SNIPARA_PROJECT_SLUG or pass project_slug parameter."
        )

    # Create client
    client = SniparaClient(api_key, project_slug, api_url)

    # Define tool handlers
    async def context_query(
        query: str,
        max_tokens: int = 4000,
        search_mode: str = "hybrid",
        include_metadata: bool = True,
    ) -> dict[str, Any]:
        """Query Snipara for optimized, relevant context.

        Args:
            query: The question or topic to search for
            max_tokens: Maximum tokens to return (default: 4000)
            search_mode: Search mode - keyword, semantic, or hybrid
            include_metadata: Include file paths and relevance scores

        Returns:
            Dictionary with sections, total_tokens, and suggestions
        """
        return await client.call_tool("rlm_context_query", {
            "query": query,
            "max_tokens": max_tokens,
            "search_mode": search_mode,
            "include_metadata": include_metadata,
        })

    async def sections() -> dict[str, Any]:
        """List all available documentation sections.

        Returns:
            Dictionary with sections list containing paths and chunk counts
        """
        return await client.call_tool("rlm_sections", {})

    async def search(
        pattern: str,
        max_results: int = 20,
    ) -> dict[str, Any]:
        """Search documentation for a regex pattern.

        Args:
            pattern: Regex pattern to search for
            max_results: Maximum number of results

        Returns:
            Dictionary with matches list
        """
        return await client.call_tool("rlm_search", {
            "pattern": pattern,
            "max_results": max_results,
        })

    async def read(
        file: str,
        start_line: int = 1,
        end_line: int | None = None,
    ) -> dict[str, Any]:
        """Read specific lines from a documentation file.

        Args:
            file: File path to read
            start_line: Starting line number (default: 1)
            end_line: Ending line number (optional, reads to end if not specified)

        Returns:
            Dictionary with content string
        """
        params: dict[str, Any] = {"file": file, "start_line": start_line}
        if end_line is not None:
            params["end_line"] = end_line
        return await client.call_tool("rlm_read", params)

    async def shared_context(
        max_tokens: int = 4000,
        categories: list[str] | None = None,
        include_content: bool = True,
    ) -> dict[str, Any]:
        """Get merged context from linked shared collections.

        Returns team best practices, coding standards, and guidelines
        organized by priority category.

        Args:
            max_tokens: Token budget for context
            categories: Filter to specific categories (MANDATORY, BEST_PRACTICES, etc.)
            include_content: Include the actual content

        Returns:
            Dictionary with documents, collections_loaded, and merged_content
        """
        params: dict[str, Any] = {
            "max_tokens": max_tokens,
            "include_content": include_content,
        }
        if categories:
            params["categories"] = categories
        return await client.call_tool("rlm_shared_context", params)

    async def decompose(
        query: str,
        max_depth: int = 2,
    ) -> dict[str, Any]:
        """Break a complex query into sub-queries with execution order.

        Args:
            query: Complex question to decompose
            max_depth: Maximum decomposition depth

        Returns:
            Dictionary with sub_queries and suggested_sequence
        """
        return await client.call_tool("rlm_decompose", {
            "query": query,
            "max_depth": max_depth,
        })

    async def multi_query(
        queries: list[dict[str, str]],
        max_tokens: int = 8000,
    ) -> dict[str, Any]:
        """Execute multiple queries with shared token budget.

        Args:
            queries: List of query objects with 'query' key
            max_tokens: Total token budget

        Returns:
            Dictionary with results for each query
        """
        return await client.call_tool("rlm_multi_query", {
            "queries": queries,
            "max_tokens": max_tokens,
        })

    async def multi_project_query(
        query: str,
        max_tokens: int = 4000,
        per_project_limit: int = 3,
        project_ids: list[str] | None = None,
        exclude_project_ids: list[str] | None = None,
        search_mode: str = "keyword",
        include_metadata: bool = True,
    ) -> dict[str, Any]:
        """Query across multiple projects in your team.

        Args:
            query: The query/question to get context for
            max_tokens: Maximum tokens to return across all projects
            per_project_limit: Maximum sections to return per project
            project_ids: Optional list of project IDs or slugs to include
            exclude_project_ids: Optional list of project IDs or slugs to exclude
            search_mode: Search strategy (keyword, semantic, hybrid)
            include_metadata: Include file paths, line numbers, and relevance scores

        Returns:
            Dictionary with results from multiple projects
        """
        params: dict[str, Any] = {
            "query": query,
            "max_tokens": max_tokens,
            "per_project_limit": per_project_limit,
            "search_mode": search_mode,
            "include_metadata": include_metadata,
        }
        if project_ids:
            params["project_ids"] = project_ids
        if exclude_project_ids:
            params["exclude_project_ids"] = exclude_project_ids
        return await client.call_tool("rlm_multi_project_query", params)

    async def stats() -> dict[str, Any]:
        """Get documentation statistics.

        Returns:
            Dictionary with files_loaded, total_lines, total_characters, sections
        """
        return await client.call_tool("rlm_stats", {})

    async def list_templates(
        category: str | None = None,
    ) -> dict[str, Any]:
        """List available prompt templates from shared collections.

        Args:
            category: Optional category filter

        Returns:
            Dictionary with templates list
        """
        params: dict[str, Any] = {}
        if category:
            params["category"] = category
        return await client.call_tool("rlm_list_templates", params)

    async def get_template(
        template_id: str | None = None,
        slug: str | None = None,
        variables: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Get and optionally render a prompt template.

        Args:
            template_id: Template ID
            slug: Template slug (alternative to ID)
            variables: Variables to substitute in template

        Returns:
            Dictionary with template and rendered_prompt
        """
        params: dict[str, Any] = {}
        if template_id:
            params["template_id"] = template_id
        if slug:
            params["slug"] = slug
        if variables:
            params["variables"] = variables
        return await client.call_tool("rlm_get_template", params)

    # ============ SESSION MANAGEMENT TOOLS ============

    async def ask(question: str) -> dict[str, Any]:
        """Basic documentation query.

        Args:
            question: The question to ask about the documentation

        Returns:
            Dictionary with answer
        """
        return await client.call_tool("rlm_ask", {"question": question})

    async def inject(context: str, append: bool = False) -> dict[str, Any]:
        """Inject context into the session.

        Args:
            context: The context to inject
            append: Append to existing context instead of replacing

        Returns:
            Dictionary with success status
        """
        return await client.call_tool("rlm_inject", {
            "context": context,
            "append": append,
        })

    async def get_context() -> dict[str, Any]:
        """Get the current session context.

        Returns:
            Dictionary with current context
        """
        return await client.call_tool("rlm_context", {})

    async def clear_context() -> dict[str, Any]:
        """Clear the current session context.

        Returns:
            Dictionary with success status
        """
        return await client.call_tool("rlm_clear_context", {})

    async def get_settings() -> dict[str, Any]:
        """Get project settings.

        Returns:
            Dictionary with project settings
        """
        return await client.call_tool("rlm_settings", {})

    async def plan(
        query: str,
        strategy: str = "relevance_first",
        max_tokens: int = 16000,
    ) -> dict[str, Any]:
        """Create an execution plan for a complex query.

        Args:
            query: The complex question to plan for
            strategy: Execution strategy (breadth_first, depth_first, relevance_first)
            max_tokens: Total token budget

        Returns:
            Dictionary with plan steps
        """
        return await client.call_tool("rlm_plan", {
            "query": query,
            "strategy": strategy,
            "max_tokens": max_tokens,
        })

    # ============ SUMMARY STORAGE TOOLS ============

    async def store_summary(
        document_path: str,
        summary: str,
        summary_type: str = "concise",
        section_id: str | None = None,
        line_start: int | None = None,
        line_end: int | None = None,
        generated_by: str | None = None,
    ) -> dict[str, Any]:
        """Store a summary for a document or section.

        Args:
            document_path: Path to the document
            summary: The summary text to store
            summary_type: Type of summary (concise, detailed, technical, keywords, custom)
            section_id: Optional section identifier
            line_start: Start line for section summary
            line_end: End line for section summary
            generated_by: Model that generated the summary

        Returns:
            Dictionary with summary_id and status
        """
        params: dict[str, Any] = {
            "document_path": document_path,
            "summary": summary,
            "summary_type": summary_type,
        }
        if section_id:
            params["section_id"] = section_id
        if line_start is not None:
            params["line_start"] = line_start
        if line_end is not None:
            params["line_end"] = line_end
        if generated_by:
            params["generated_by"] = generated_by
        return await client.call_tool("rlm_store_summary", params)

    async def get_summaries(
        document_path: str | None = None,
        summary_type: str | None = None,
        section_id: str | None = None,
        include_content: bool = True,
    ) -> dict[str, Any]:
        """Get stored summaries.

        Args:
            document_path: Filter by document path
            summary_type: Filter by summary type
            section_id: Filter by section ID
            include_content: Include summary content in response

        Returns:
            Dictionary with summaries list
        """
        params: dict[str, Any] = {"include_content": include_content}
        if document_path:
            params["document_path"] = document_path
        if summary_type:
            params["summary_type"] = summary_type
        if section_id:
            params["section_id"] = section_id
        return await client.call_tool("rlm_get_summaries", params)

    async def delete_summary(
        summary_id: str | None = None,
        document_path: str | None = None,
        summary_type: str | None = None,
    ) -> dict[str, Any]:
        """Delete stored summaries.

        Args:
            summary_id: Specific summary ID to delete
            document_path: Delete all summaries for document
            summary_type: Delete summaries of this type

        Returns:
            Dictionary with deleted count
        """
        params: dict[str, Any] = {}
        if summary_id:
            params["summary_id"] = summary_id
        if document_path:
            params["document_path"] = document_path
        if summary_type:
            params["summary_type"] = summary_type
        return await client.call_tool("rlm_delete_summary", params)

    # ============ AGENT MEMORY TOOLS ============

    async def remember(
        content: str,
        type: str = "fact",
        scope: str = "project",
        category: str | None = None,
        ttl_days: int | None = None,
        related_to: list[str] | None = None,
        document_refs: list[str] | None = None,
        source: str | None = None,
    ) -> dict[str, Any]:
        """Store a memory.

        Args:
            content: The memory content to store
            type: Memory type (fact, decision, learning, preference, todo, context)
            scope: Visibility scope (agent, project, team, user)
            category: Optional grouping category
            ttl_days: Days until memory expires (null = permanent)
            related_to: IDs of related memories
            document_refs: Referenced document paths
            source: What created this memory

        Returns:
            Dictionary with memory_id and status
        """
        params: dict[str, Any] = {
            "content": content,
            "type": type,
            "scope": scope,
        }
        if category:
            params["category"] = category
        if ttl_days is not None:
            params["ttl_days"] = ttl_days
        if related_to:
            params["related_to"] = related_to
        if document_refs:
            params["document_refs"] = document_refs
        if source:
            params["source"] = source
        return await client.call_tool("rlm_remember", params)

    async def recall(
        query: str,
        type: str | None = None,
        scope: str | None = None,
        category: str | None = None,
        limit: int = 5,
        min_relevance: float = 0.5,
        include_expired: bool = False,
    ) -> dict[str, Any]:
        """Recall memories semantically.

        Args:
            query: Search query for semantic recall
            type: Filter by memory type
            scope: Filter by scope
            category: Filter by category
            limit: Maximum memories to return
            min_relevance: Minimum relevance score (0-1)
            include_expired: Include expired memories

        Returns:
            Dictionary with recalled memories
        """
        params: dict[str, Any] = {
            "query": query,
            "limit": limit,
            "min_relevance": min_relevance,
            "include_expired": include_expired,
        }
        if type:
            params["type"] = type
        if scope:
            params["scope"] = scope
        if category:
            params["category"] = category
        return await client.call_tool("rlm_recall", params)

    async def memories(
        type: str | None = None,
        scope: str | None = None,
        category: str | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
        include_expired: bool = False,
    ) -> dict[str, Any]:
        """List stored memories.

        Args:
            type: Filter by memory type
            scope: Filter by scope
            category: Filter by category
            search: Text search in content
            limit: Maximum memories to return
            offset: Offset for pagination
            include_expired: Include expired memories

        Returns:
            Dictionary with memories list
        """
        params: dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "include_expired": include_expired,
        }
        if type:
            params["type"] = type
        if scope:
            params["scope"] = scope
        if category:
            params["category"] = category
        if search:
            params["search"] = search
        return await client.call_tool("rlm_memories", params)

    async def forget(
        memory_id: str | None = None,
        type: str | None = None,
        category: str | None = None,
        older_than_days: int | None = None,
    ) -> dict[str, Any]:
        """Delete memories.

        Args:
            memory_id: Specific memory ID to delete
            type: Delete all memories of this type
            category: Delete all memories in this category
            older_than_days: Delete memories older than N days

        Returns:
            Dictionary with deleted count
        """
        params: dict[str, Any] = {}
        if memory_id:
            params["memory_id"] = memory_id
        if type:
            params["type"] = type
        if category:
            params["category"] = category
        if older_than_days is not None:
            params["older_than_days"] = older_than_days
        return await client.call_tool("rlm_forget", params)

    # ============ SWARM COORDINATION TOOLS ============

    async def swarm_create(
        name: str,
        description: str | None = None,
        max_agents: int = 10,
        task_timeout: int = 300,
        claim_timeout: int = 600,
    ) -> dict[str, Any]:
        """Create a new agent swarm.

        Args:
            name: Swarm name
            description: Swarm description
            max_agents: Maximum agents allowed (2-50)
            task_timeout: Task timeout in seconds
            claim_timeout: Resource claim timeout in seconds

        Returns:
            Dictionary with swarm_id
        """
        params: dict[str, Any] = {
            "name": name,
            "max_agents": max_agents,
            "task_timeout": task_timeout,
            "claim_timeout": claim_timeout,
        }
        if description:
            params["description"] = description
        return await client.call_tool("rlm_swarm_create", params)

    async def swarm_join(
        swarm_id: str,
        agent_id: str,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Join an existing swarm.

        Args:
            swarm_id: ID of swarm to join
            agent_id: Unique identifier for this agent
            name: Human-readable agent name

        Returns:
            Dictionary with join status
        """
        params: dict[str, Any] = {
            "swarm_id": swarm_id,
            "agent_id": agent_id,
        }
        if name:
            params["name"] = name
        return await client.call_tool("rlm_swarm_join", params)

    async def claim(
        swarm_id: str,
        agent_id: str,
        resource_type: str,
        resource_id: str,
        ttl_seconds: int | None = None,
    ) -> dict[str, Any]:
        """Claim exclusive access to a resource.

        Args:
            swarm_id: Swarm ID
            agent_id: Agent ID making the claim
            resource_type: Resource type (file, function, module, custom)
            resource_id: Resource identifier (e.g., 'src/auth.ts')
            ttl_seconds: Custom TTL (uses swarm default if null)

        Returns:
            Dictionary with claim status
        """
        params: dict[str, Any] = {
            "swarm_id": swarm_id,
            "agent_id": agent_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
        }
        if ttl_seconds is not None:
            params["ttl_seconds"] = ttl_seconds
        return await client.call_tool("rlm_claim", params)

    async def release(
        swarm_id: str,
        agent_id: str,
        resource_type: str,
        resource_id: str,
    ) -> dict[str, Any]:
        """Release a claimed resource.

        Args:
            swarm_id: Swarm ID
            agent_id: Agent ID releasing the claim
            resource_type: Resource type
            resource_id: Resource identifier

        Returns:
            Dictionary with release status
        """
        return await client.call_tool("rlm_release", {
            "swarm_id": swarm_id,
            "agent_id": agent_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
        })

    async def state_get(swarm_id: str, key: str) -> dict[str, Any]:
        """Get shared swarm state.

        Args:
            swarm_id: Swarm ID
            key: State key to retrieve

        Returns:
            Dictionary with state value
        """
        return await client.call_tool("rlm_state_get", {
            "swarm_id": swarm_id,
            "key": key,
        })

    async def state_set(
        swarm_id: str,
        agent_id: str,
        key: str,
        value: Any,
        expected_version: int | None = None,
    ) -> dict[str, Any]:
        """Set shared swarm state.

        Args:
            swarm_id: Swarm ID
            agent_id: Agent ID setting the state
            key: State key
            value: State value (JSON-serializable)
            expected_version: Expected version for optimistic locking

        Returns:
            Dictionary with set status
        """
        params: dict[str, Any] = {
            "swarm_id": swarm_id,
            "agent_id": agent_id,
            "key": key,
            "value": value,
        }
        if expected_version is not None:
            params["expected_version"] = expected_version
        return await client.call_tool("rlm_state_set", params)

    async def broadcast(
        swarm_id: str,
        agent_id: str,
        event_type: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Broadcast an event to the swarm.

        Args:
            swarm_id: Swarm ID
            agent_id: Agent ID broadcasting
            event_type: Event type (e.g., 'file_changed', 'task_done')
            payload: Event payload

        Returns:
            Dictionary with broadcast status
        """
        return await client.call_tool("rlm_broadcast", {
            "swarm_id": swarm_id,
            "agent_id": agent_id,
            "event_type": event_type,
            "payload": payload or {},
        })

    async def task_create(
        swarm_id: str,
        title: str,
        description: str | None = None,
        priority: int = 0,
        depends_on: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a task in the swarm.

        Args:
            swarm_id: Swarm ID
            title: Task title
            description: Task description
            priority: Priority (higher = more urgent)
            depends_on: Task IDs that must complete first

        Returns:
            Dictionary with task_id
        """
        params: dict[str, Any] = {
            "swarm_id": swarm_id,
            "title": title,
            "priority": priority,
        }
        if description:
            params["description"] = description
        if depends_on:
            params["depends_on"] = depends_on
        return await client.call_tool("rlm_task_create", params)

    async def task_claim(
        swarm_id: str,
        agent_id: str,
        task_id: str | None = None,
    ) -> dict[str, Any]:
        """Claim a task from the swarm queue.

        Args:
            swarm_id: Swarm ID
            agent_id: Agent ID claiming
            task_id: Specific task ID (null = get next available)

        Returns:
            Dictionary with claimed task
        """
        params: dict[str, Any] = {
            "swarm_id": swarm_id,
            "agent_id": agent_id,
        }
        if task_id:
            params["task_id"] = task_id
        return await client.call_tool("rlm_task_claim", params)

    async def task_complete(
        swarm_id: str,
        agent_id: str,
        task_id: str,
        result: dict[str, Any] | None = None,
        error: str | None = None,
    ) -> dict[str, Any]:
        """Complete a task.

        Args:
            swarm_id: Swarm ID
            agent_id: Agent ID completing
            task_id: Task ID to complete
            result: Task result data
            error: Error message if task failed

        Returns:
            Dictionary with completion status
        """
        params: dict[str, Any] = {
            "swarm_id": swarm_id,
            "agent_id": agent_id,
            "task_id": task_id,
        }
        if result:
            params["result"] = result
        if error:
            params["error"] = error
        return await client.call_tool("rlm_task_complete", params)

    # ============ DOCUMENT MANAGEMENT TOOLS ============

    async def upload_document(
        path: str,
        content: str,
    ) -> dict[str, Any]:
        """Upload a document.

        Args:
            path: Document path
            content: Document content

        Returns:
            Dictionary with upload status
        """
        return await client.call_tool("rlm_upload_document", {
            "path": path,
            "content": content,
        })

    async def sync_documents(
        documents: list[dict[str, str]],
        delete_missing: bool = False,
    ) -> dict[str, Any]:
        """Sync multiple documents.

        Args:
            documents: List of documents with path and content
            delete_missing: Delete documents not in list

        Returns:
            Dictionary with sync stats
        """
        return await client.call_tool("rlm_sync_documents", {
            "documents": documents,
            "delete_missing": delete_missing,
        })

    # Build and return tool list
    return [
        Tool(
            name="context_query",
            description=(
                "Query Snipara for optimized, relevant context. "
                "Returns the most relevant documentation sections within your token budget. "
                "This is the PRIMARY tool for any documentation questions. "
                "Uses hybrid search (keyword + semantic) by default for best results."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The question or topic to search for",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "default": 4000,
                        "description": "Maximum tokens to return",
                    },
                    "search_mode": {
                        "type": "string",
                        "enum": ["keyword", "semantic", "hybrid"],
                        "default": "hybrid",
                        "description": "Search mode",
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include file paths and relevance scores",
                    },
                },
                "required": ["query"],
            },
            handler=context_query,
        ),
        Tool(
            name="sections",
            description=(
                "List all available documentation sections in the project. "
                "Returns file paths and chunk counts for each document."
            ),
            parameters={
                "type": "object",
                "properties": {},
            },
            handler=sections,
        ),
        Tool(
            name="search",
            description=(
                "Search documentation for a regex pattern. "
                "Returns matching lines with file paths and line numbers."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for",
                    },
                    "max_results": {
                        "type": "integer",
                        "default": 20,
                        "description": "Maximum number of results",
                    },
                },
                "required": ["pattern"],
            },
            handler=search,
        ),
        Tool(
            name="read",
            description=(
                "Read specific lines from a documentation file. "
                "Use after search or sections to get full content."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "File path to read",
                    },
                    "start_line": {
                        "type": "integer",
                        "default": 1,
                        "description": "Starting line number (default: 1)",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Ending line number (optional)",
                    },
                },
                "required": ["file"],
            },
            handler=read,
        ),
        Tool(
            name="shared_context",
            description=(
                "Get merged context from linked shared collections. "
                "Returns team best practices, coding standards, and guidelines "
                "organized by priority (MANDATORY > BEST_PRACTICES > GUIDELINES > REFERENCE). "
                "Use this to ensure code follows team conventions."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "max_tokens": {
                        "type": "integer",
                        "default": 4000,
                        "description": "Token budget for context",
                    },
                    "categories": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["MANDATORY", "BEST_PRACTICES", "GUIDELINES", "REFERENCE"],
                        },
                        "description": "Filter to specific categories",
                    },
                    "include_content": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include the actual content",
                    },
                },
            },
            handler=shared_context,
        ),
        Tool(
            name="decompose",
            description=(
                "Break a complex query into sub-queries with execution order. "
                "Use for multi-part questions that need to be answered step by step."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Complex question to decompose",
                    },
                    "max_depth": {
                        "type": "integer",
                        "default": 2,
                        "description": "Maximum decomposition depth",
                    },
                },
                "required": ["query"],
            },
            handler=decompose,
        ),
        Tool(
            name="multi_query",
            description=(
                "Execute multiple queries with shared token budget. "
                "More efficient than calling context_query multiple times."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "queries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                            },
                            "required": ["query"],
                        },
                        "description": "List of queries to execute",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "default": 8000,
                        "description": "Total token budget",
                    },
                },
                "required": ["queries"],
            },
            handler=multi_query,
        ),
        Tool(
            name="multi_project_query",
            description=(
                "Query across multiple projects in your team. "
                "Useful for finding context across related codebases or shared documentation."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query/question to get context for",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "default": 4000,
                        "description": "Maximum tokens to return across all projects",
                    },
                    "per_project_limit": {
                        "type": "integer",
                        "default": 3,
                        "description": "Maximum sections to return per project",
                    },
                    "project_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of project IDs or slugs to include",
                    },
                    "exclude_project_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of project IDs or slugs to exclude",
                    },
                    "search_mode": {
                        "type": "string",
                        "enum": ["keyword", "semantic", "hybrid"],
                        "default": "keyword",
                        "description": "Search strategy",
                    },
                    "include_metadata": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include file paths, line numbers, and relevance scores",
                    },
                },
                "required": ["query"],
            },
            handler=multi_project_query,
        ),
        Tool(
            name="stats",
            description=(
                "Get documentation statistics. "
                "Returns file count, line count, and section count."
            ),
            parameters={
                "type": "object",
                "properties": {},
            },
            handler=stats,
        ),
        Tool(
            name="list_templates",
            description=(
                "List available prompt templates from shared collections. "
                "Templates can be used with get_template to generate prompts."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category",
                    },
                },
            },
            handler=list_templates,
        ),
        Tool(
            name="get_template",
            description=(
                "Get and optionally render a prompt template. "
                "Pass variables to substitute placeholders in the template."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "Template ID",
                    },
                    "slug": {
                        "type": "string",
                        "description": "Template slug (alternative to ID)",
                    },
                    "variables": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "Variables to substitute",
                    },
                },
            },
            handler=get_template,
        ),
        # ============ SESSION MANAGEMENT TOOLS ============
        Tool(
            name="ask",
            description=(
                "Basic documentation query. "
                "Ask a question and get an answer based on the documentation."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to ask about the documentation",
                    },
                },
                "required": ["question"],
            },
            handler=ask,
        ),
        Tool(
            name="inject",
            description=(
                "Inject context into the session. "
                "This context will be included in subsequent queries."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "The context to inject",
                    },
                    "append": {
                        "type": "boolean",
                        "default": False,
                        "description": "Append to existing context instead of replacing",
                    },
                },
                "required": ["context"],
            },
            handler=inject,
        ),
        Tool(
            name="context",
            description=(
                "Get the current session context. "
                "Returns any context that was previously injected."
            ),
            parameters={
                "type": "object",
                "properties": {},
            },
            handler=get_context,
        ),
        Tool(
            name="clear_context",
            description=(
                "Clear the current session context. "
                "Removes any previously injected context."
            ),
            parameters={
                "type": "object",
                "properties": {},
            },
            handler=clear_context,
        ),
        Tool(
            name="settings",
            description=(
                "Get project settings. "
                "Returns configuration like max tokens, search mode, etc."
            ),
            parameters={
                "type": "object",
                "properties": {},
            },
            handler=get_settings,
        ),
        Tool(
            name="plan",
            description=(
                "Create an execution plan for a complex query. "
                "Returns a sequence of steps to answer complex multi-part questions."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The complex question to plan for",
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["breadth_first", "depth_first", "relevance_first"],
                        "default": "relevance_first",
                        "description": "Execution strategy",
                    },
                    "max_tokens": {
                        "type": "integer",
                        "default": 16000,
                        "description": "Total token budget",
                    },
                },
                "required": ["query"],
            },
            handler=plan,
        ),
        # ============ SUMMARY STORAGE TOOLS ============
        Tool(
            name="store_summary",
            description=(
                "Store a summary for a document or section. "
                "Summaries are used to provide concise context in queries."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "document_path": {
                        "type": "string",
                        "description": "Path to the document",
                    },
                    "summary": {
                        "type": "string",
                        "description": "The summary text to store",
                    },
                    "summary_type": {
                        "type": "string",
                        "enum": ["concise", "detailed", "technical", "keywords", "custom"],
                        "default": "concise",
                        "description": "Type of summary",
                    },
                    "section_id": {
                        "type": "string",
                        "description": "Optional section identifier",
                    },
                    "line_start": {
                        "type": "integer",
                        "description": "Start line for section summary",
                    },
                    "line_end": {
                        "type": "integer",
                        "description": "End line for section summary",
                    },
                    "generated_by": {
                        "type": "string",
                        "description": "Model that generated the summary",
                    },
                },
                "required": ["document_path", "summary"],
            },
            handler=store_summary,
        ),
        Tool(
            name="get_summaries",
            description=(
                "Get stored summaries. "
                "Filter by document path, type, or section."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "document_path": {
                        "type": "string",
                        "description": "Filter by document path",
                    },
                    "summary_type": {
                        "type": "string",
                        "enum": ["concise", "detailed", "technical", "keywords", "custom"],
                        "description": "Filter by summary type",
                    },
                    "section_id": {
                        "type": "string",
                        "description": "Filter by section ID",
                    },
                    "include_content": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include summary content in response",
                    },
                },
            },
            handler=get_summaries,
        ),
        Tool(
            name="delete_summary",
            description=(
                "Delete stored summaries. "
                "Delete by ID, document path, or type."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "summary_id": {
                        "type": "string",
                        "description": "Specific summary ID to delete",
                    },
                    "document_path": {
                        "type": "string",
                        "description": "Delete all summaries for document",
                    },
                    "summary_type": {
                        "type": "string",
                        "enum": ["concise", "detailed", "technical", "keywords", "custom"],
                        "description": "Delete summaries of this type",
                    },
                },
            },
            handler=delete_summary,
        ),
        # ============ AGENT MEMORY TOOLS ============
        Tool(
            name="remember",
            description=(
                "Store a memory for later recall. "
                "Memories can be facts, decisions, learnings, preferences, todos, or context. "
                "Use this to persist important information across sessions."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The memory content to store",
                    },
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
                    "category": {
                        "type": "string",
                        "description": "Optional grouping category",
                    },
                    "ttl_days": {
                        "type": "integer",
                        "description": "Days until memory expires (null = permanent)",
                    },
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
                    "source": {
                        "type": "string",
                        "description": "What created this memory",
                    },
                },
                "required": ["content"],
            },
            handler=remember,
        ),
        Tool(
            name="recall",
            description=(
                "Recall memories semantically. "
                "Search for relevant memories using natural language queries."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for semantic recall",
                    },
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
                    "category": {
                        "type": "string",
                        "description": "Filter by category",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 5,
                        "description": "Maximum memories to return",
                    },
                    "min_relevance": {
                        "type": "number",
                        "default": 0.5,
                        "description": "Minimum relevance score (0-1)",
                    },
                    "include_expired": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include expired memories",
                    },
                },
                "required": ["query"],
            },
            handler=recall,
        ),
        Tool(
            name="memories",
            description=(
                "List stored memories with filters. "
                "Browse memories by type, scope, category, or search text."
            ),
            parameters={
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
                    "category": {
                        "type": "string",
                        "description": "Filter by category",
                    },
                    "search": {
                        "type": "string",
                        "description": "Text search in content",
                    },
                    "limit": {
                        "type": "integer",
                        "default": 20,
                        "description": "Maximum memories to return",
                    },
                    "offset": {
                        "type": "integer",
                        "default": 0,
                        "description": "Offset for pagination",
                    },
                    "include_expired": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include expired memories",
                    },
                },
            },
            handler=memories,
        ),
        Tool(
            name="forget",
            description=(
                "Delete memories. "
                "Remove memories by ID, type, category, or age."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "Specific memory ID to delete",
                    },
                    "type": {
                        "type": "string",
                        "enum": ["fact", "decision", "learning", "preference", "todo", "context"],
                        "description": "Delete all memories of this type",
                    },
                    "category": {
                        "type": "string",
                        "description": "Delete all memories in this category",
                    },
                    "older_than_days": {
                        "type": "integer",
                        "description": "Delete memories older than N days",
                    },
                },
            },
            handler=forget,
        ),
        # ============ SWARM COORDINATION TOOLS ============
        Tool(
            name="swarm_create",
            description=(
                "Create a new agent swarm. "
                "Swarms allow multiple agents to coordinate on a shared task."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Swarm name",
                    },
                    "description": {
                        "type": "string",
                        "description": "Swarm description",
                    },
                    "max_agents": {
                        "type": "integer",
                        "default": 10,
                        "description": "Maximum agents allowed (2-50)",
                    },
                    "task_timeout": {
                        "type": "integer",
                        "default": 300,
                        "description": "Task timeout in seconds",
                    },
                    "claim_timeout": {
                        "type": "integer",
                        "default": 600,
                        "description": "Resource claim timeout in seconds",
                    },
                },
                "required": ["name"],
            },
            handler=swarm_create,
        ),
        Tool(
            name="swarm_join",
            description=(
                "Join an existing swarm. "
                "Agents must join a swarm before claiming resources or tasks."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "swarm_id": {
                        "type": "string",
                        "description": "ID of swarm to join",
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Unique identifier for this agent",
                    },
                    "name": {
                        "type": "string",
                        "description": "Human-readable agent name",
                    },
                },
                "required": ["swarm_id", "agent_id"],
            },
            handler=swarm_join,
        ),
        Tool(
            name="claim",
            description=(
                "Claim exclusive access to a resource. "
                "Prevents other agents from modifying the same file/function."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "swarm_id": {
                        "type": "string",
                        "description": "Swarm ID",
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID making the claim",
                    },
                    "resource_type": {
                        "type": "string",
                        "description": "Resource type (file, function, module, custom)",
                    },
                    "resource_id": {
                        "type": "string",
                        "description": "Resource identifier (e.g., 'src/auth.ts')",
                    },
                    "ttl_seconds": {
                        "type": "integer",
                        "description": "Custom TTL (uses swarm default if null)",
                    },
                },
                "required": ["swarm_id", "agent_id", "resource_type", "resource_id"],
            },
            handler=claim,
        ),
        Tool(
            name="release",
            description=(
                "Release a claimed resource. "
                "Allows other agents to claim the resource."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "swarm_id": {
                        "type": "string",
                        "description": "Swarm ID",
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID releasing the claim",
                    },
                    "resource_type": {
                        "type": "string",
                        "description": "Resource type",
                    },
                    "resource_id": {
                        "type": "string",
                        "description": "Resource identifier",
                    },
                },
                "required": ["swarm_id", "agent_id", "resource_type", "resource_id"],
            },
            handler=release,
        ),
        Tool(
            name="state_get",
            description=(
                "Get shared swarm state. "
                "Retrieve a value from the shared state store."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "swarm_id": {
                        "type": "string",
                        "description": "Swarm ID",
                    },
                    "key": {
                        "type": "string",
                        "description": "State key to retrieve",
                    },
                },
                "required": ["swarm_id", "key"],
            },
            handler=state_get,
        ),
        Tool(
            name="state_set",
            description=(
                "Set shared swarm state. "
                "Store a value in the shared state store with optional optimistic locking."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "swarm_id": {
                        "type": "string",
                        "description": "Swarm ID",
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID setting the state",
                    },
                    "key": {
                        "type": "string",
                        "description": "State key",
                    },
                    "value": {
                        "description": "State value (JSON-serializable)",
                    },
                    "expected_version": {
                        "type": "integer",
                        "description": "Expected version for optimistic locking",
                    },
                },
                "required": ["swarm_id", "agent_id", "key", "value"],
            },
            handler=state_set,
        ),
        Tool(
            name="broadcast",
            description=(
                "Broadcast an event to the swarm. "
                "Notify other agents about changes or completions."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "swarm_id": {
                        "type": "string",
                        "description": "Swarm ID",
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID broadcasting",
                    },
                    "event_type": {
                        "type": "string",
                        "description": "Event type (e.g., 'file_changed', 'task_done')",
                    },
                    "payload": {
                        "type": "object",
                        "description": "Event payload",
                    },
                },
                "required": ["swarm_id", "agent_id", "event_type"],
            },
            handler=broadcast,
        ),
        Tool(
            name="task_create",
            description=(
                "Create a task in the swarm. "
                "Tasks can be claimed and completed by agents."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "swarm_id": {
                        "type": "string",
                        "description": "Swarm ID",
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title",
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description",
                    },
                    "priority": {
                        "type": "integer",
                        "default": 0,
                        "description": "Priority (higher = more urgent)",
                    },
                    "depends_on": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Task IDs that must complete first",
                    },
                },
                "required": ["swarm_id", "title"],
            },
            handler=task_create,
        ),
        Tool(
            name="task_claim",
            description=(
                "Claim a task from the swarm queue. "
                "Returns the next available task or a specific task."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "swarm_id": {
                        "type": "string",
                        "description": "Swarm ID",
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID claiming",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Specific task ID (null = get next available)",
                    },
                },
                "required": ["swarm_id", "agent_id"],
            },
            handler=task_claim,
        ),
        Tool(
            name="task_complete",
            description=(
                "Complete a task. "
                "Mark a claimed task as done with optional result or error."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "swarm_id": {
                        "type": "string",
                        "description": "Swarm ID",
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID completing",
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task ID to complete",
                    },
                    "result": {
                        "type": "object",
                        "description": "Task result data",
                    },
                    "error": {
                        "type": "string",
                        "description": "Error message if task failed",
                    },
                },
                "required": ["swarm_id", "agent_id", "task_id"],
            },
            handler=task_complete,
        ),
        # ============ DOCUMENT MANAGEMENT TOOLS ============
        Tool(
            name="upload_document",
            description=(
                "Upload a document to the project. "
                "Creates or updates a document in the documentation store."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Document path",
                    },
                    "content": {
                        "type": "string",
                        "description": "Document content",
                    },
                },
                "required": ["path", "content"],
            },
            handler=upload_document,
        ),
        Tool(
            name="sync_documents",
            description=(
                "Sync multiple documents. "
                "Bulk create/update/delete documents to match provided list."
            ),
            parameters={
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
                        "description": "List of documents with path and content",
                    },
                    "delete_missing": {
                        "type": "boolean",
                        "default": False,
                        "description": "Delete documents not in list",
                    },
                },
                "required": ["documents"],
            },
            handler=sync_documents,
        ),
    ]
