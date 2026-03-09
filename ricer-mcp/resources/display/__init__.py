"""Display resources — read-only views of display-related Plasma settings."""

from .get_wallpaper import register as register_wallpaper
from .get_panel_position import register as register_panel
from .get_global_scaling import register as register_scaling
from .get_window_borders import register as register_borders


def register_all(mcp):
    """Register all display resource endpoints on the MCP server."""
    register_wallpaper(mcp)
    register_panel(mcp)
    register_scaling(mcp)
    register_borders(mcp)
