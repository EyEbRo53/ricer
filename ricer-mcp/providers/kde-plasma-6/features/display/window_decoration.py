"""Feature: window decoration (display)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class WindowDecorationFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, theme: str) -> bool:
        """Set KDE Plasma window decoration theme via kwriteconfig6."""
        return write_kde_config("kdeglobals", "WM", "theme", theme)

    def get(self) -> dict:
        """Return current window decoration theme as a structured payload."""
        value = read_kde_config("kdeglobals", "WM", "theme", "")
        return {
            "setting": "window_decoration",
            "file": "kdeglobals",
            "group": "WM",
            "key": "theme",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_window_decoration(theme: str) -> str:
            """Stage a window decoration theme change."""
            import json
            receipt = changeset.add("window_decoration", {"theme": theme})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_window_decoration() -> dict:
            """Return current window decoration setting."""
            return self.get()
