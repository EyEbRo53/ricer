"""Feature: menu opacity (display)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class MenuOpacityFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, opacity: float) -> bool:
        """Set KDE Plasma menu opacity via kwriteconfig6."""
        return write_kde_config("kdeglobals", "KDE", "MenuOpacity", str(opacity))

    def get(self) -> dict:
        """Return current menu opacity as a structured payload."""
        value = read_kde_config("kdeglobals", "KDE", "MenuOpacity", "1.0")
        try:
            value = float(value)
        except (TypeError, ValueError):
            pass
        return {
            "setting": "menu_opacity",
            "file": "kdeglobals",
            "group": "KDE",
            "key": "MenuOpacity",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_menu_opacity(opacity: float) -> str:
            """Stage a menu opacity change."""
            import json
            receipt = changeset.add("menu_opacity", {"opacity": opacity})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_menu_opacity() -> dict:
            """Return current menu opacity setting."""
            return self.get()
