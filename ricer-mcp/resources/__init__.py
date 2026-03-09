"""Top-level resources package — registers all read-only Plasma resources."""

from .input import register_all as register_input_resources
from .display import register_all as register_display_resources


def register_all(mcp):
    """Register every read-only resource on the MCP server."""
    register_input_resources(mcp)
    register_display_resources(mcp)
