"""Display tools — staging tools for changes that apply live or after KWin reconfigure."""

from .set_color_scheme import register as register_color_scheme
from .set_global_scaling import register as register_scaling
from .set_window_borders import register as register_borders
from .set_wallpaper import register as register_wallpaper
from .move_panel import register as register_panel


def register_all(mcp, changeset):
    """Register all display staging tools on the MCP server."""
    register_color_scheme(mcp, changeset)
    register_scaling(mcp, changeset)
    register_borders(mcp, changeset)
    register_wallpaper(mcp, changeset)
    register_panel(mcp, changeset)
