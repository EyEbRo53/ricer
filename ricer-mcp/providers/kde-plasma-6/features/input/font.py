"""Feature: system font (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class FontFeature(Feature):
    type = FeatureType.INPUT

    def set(self, font: str) -> bool:
        """Set KDE Plasma system font via kwriteconfig6."""
        return write_kde_config("kdeglobals", "General", "font", font)

    def get(self) -> dict:
        """Return current system font as a structured payload."""
        value = read_kde_config("kdeglobals", "General", "font", "")
        return {
            "setting": "font",
            "file": "kdeglobals",
            "group": "General",
            "key": "font",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_font(font: str) -> str:
            """Stage a system font change."""
            import json
            receipt = changeset.add("font", {"font": font})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_font() -> dict:
            """Return current font setting."""
            return self.get()
