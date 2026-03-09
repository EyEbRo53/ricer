"""Input tools — staging tools for changes that require a session restart."""

from .set_cursor_size import register as register_cursor_size
from .set_double_click_interval import register as register_double_click
from .set_single_click import register as register_single_click
from .set_touchpad_settings import register as register_touchpad
from .set_keyboard_accessibility import register as register_keyboard


def register_all(mcp, changeset):
    """Register all input staging tools on the MCP server."""
    register_cursor_size(mcp, changeset)
    register_double_click(mcp, changeset)
    register_single_click(mcp, changeset)
    register_touchpad(mcp, changeset)
    register_keyboard(mcp, changeset)
