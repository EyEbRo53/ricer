"""Input resources — read-only views of input-related Plasma settings."""

from .get_cursor_size import register as register_cursor_size
from .get_double_click_interval import register as register_double_click
from .get_single_click import register as register_single_click
from .get_touchpad_settings import register as register_touchpad
from .get_keyboard_accessibility import register as register_keyboard


def register_all(mcp):
    """Register all input resource endpoints on the MCP server."""
    register_cursor_size(mcp)
    register_double_click(mcp)
    register_single_click(mcp)
    register_touchpad(mcp)
    register_keyboard(mcp)
