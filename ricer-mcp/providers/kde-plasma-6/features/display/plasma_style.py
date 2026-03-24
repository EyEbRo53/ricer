"""Feature: plasma style (display)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class PlasmaStyleFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, style: str) -> bool:
        """Set KDE Plasma widget style via kwriteconfig6."""
        return write_kde_config("kdeglobals", "KDE", "widgetStyle", style)

    def get(self) -> dict:
        """Return current plasma style as a structured payload."""
        value = read_kde_config("kdeglobals", "KDE", "widgetStyle", "")
        return {
            "setting": "plasma_style",
            "file": "kdeglobals",
            "group": "KDE",
            "key": "widgetStyle",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_plasma_style(style: str) -> str:
            """Stage a plasma style change."""
            import json
            receipt = changeset.add("plasma_style", {"style": style})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_plasma_style() -> dict:
            """Return current plasma style setting."""
            return self.get()
