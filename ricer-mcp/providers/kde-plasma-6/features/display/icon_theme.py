"""Feature: icon theme (display)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class IconThemeFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, theme: str) -> bool:
        """Set KDE Plasma icon theme via kwriteconfig6."""
        return write_kde_config("kdeglobals", "Icons", "Theme", theme)

    def get(self) -> dict:
        """Return current icon theme as a structured payload."""
        value = read_kde_config("kdeglobals", "Icons", "Theme", "")
        return {
            "setting": "icon_theme",
            "file": "kdeglobals",
            "group": "Icons",
            "key": "Theme",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_icon_theme(theme: str) -> str:
            """Stage an icon theme change."""
            import json
            receipt = changeset.add("icon_theme", {"theme": theme})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_icon_theme() -> dict:
            return self.get()
