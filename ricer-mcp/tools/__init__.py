"""Top-level tools package — registers all staging tools."""

from .input import register_all as register_input_tools
from .display import register_all as register_display_tools


def register_all(mcp, changeset):
    """Register every staging tool on the MCP server."""
    register_input_tools(mcp, changeset)
    register_display_tools(mcp, changeset)
