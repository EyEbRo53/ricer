"""Feature-oriented MCP registration (one module per setting)."""

from .cursor_size import register as register_cursor_size
from .double_click_interval import register as register_double_click
from .single_click import register as register_single_click
from .touchpad_settings import register as register_touchpad
from .keyboard_accessibility import register as register_keyboard
from .global_scaling import register as register_scaling
from .window_borders import register as register_borders
from .wallpaper import register as register_wallpaper
from .panel_position import register as register_panel


def register_all(mcp, changeset):
    """Register every feature module (tool + resource) on the MCP server."""
    register_cursor_size(mcp, changeset)
    register_double_click(mcp, changeset)
    register_single_click(mcp, changeset)
    register_touchpad(mcp, changeset)
    register_keyboard(mcp, changeset)

    register_scaling(mcp, changeset)
    register_borders(mcp, changeset)
    register_wallpaper(mcp, changeset)
    register_panel(mcp, changeset)
