"""Snipara MCP Server - Context optimization for LLMs."""

from .server import main

__version__ = "2.1.0"
__all__ = ["main", "get_snipara_tools"]


def get_snipara_tools(*args, **kwargs):
    """Get Snipara tools for rlm-runtime integration.

    This is a lazy import to avoid requiring rlm-runtime
    when using snipara-mcp as a standalone MCP server.

    See rlm_tools.get_snipara_tools for full documentation.
    """
    from .rlm_tools import get_snipara_tools as _get_snipara_tools
    return _get_snipara_tools(*args, **kwargs)
