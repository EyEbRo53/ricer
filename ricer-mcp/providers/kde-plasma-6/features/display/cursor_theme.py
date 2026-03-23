"""Feature: cursor theme (display)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class CursorThemeFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, theme: str) -> bool:
        """Set KDE Plasma cursor theme via kwriteconfig6."""
        return write_kde_config("kcminputrc", "Mouse", "cursorTheme", theme)

    def get(self) -> dict:
        """Return current cursor theme as a structured payload."""
        value = read_kde_config("kcminputrc", "Mouse", "cursorTheme", "")
        return {
            "setting": "cursor_theme",
            "file": "kcminputrc",
            "group": "Mouse",
            "key": "cursorTheme",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_cursor_theme(theme: str) -> str:
            """Stage a cursor theme change."""
            import json
            receipt = changeset.add("cursor_theme", {"theme": theme})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_cursor_theme() -> dict:
            return self.get()
