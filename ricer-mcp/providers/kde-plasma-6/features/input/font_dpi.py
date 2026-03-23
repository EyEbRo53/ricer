"""Feature: font DPI scaling (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class FontDPIFeature(Feature):
    type = FeatureType.INPUT

    def set(self, dpi: int) -> bool:
        """Set KDE Plasma font DPI via kwriteconfig6."""
        return write_kde_config("kcmfonts", "General", "forceFontDPI", str(dpi))

    def get(self) -> dict:
        """Return current font DPI as a structured payload."""
        value = read_kde_config("kcmfonts", "General", "forceFontDPI", "0")
        return {
            "setting": "font_dpi",
            "file": "kcmfonts",
            "group": "General",
            "key": "forceFontDPI",
            "value": int(value) if value and value.isdigit() else value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_font_dpi(dpi: int) -> str:
            """Stage a font DPI change."""
            import json
            receipt = changeset.add("font_dpi", {"dpi": dpi})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_font_dpi() -> dict:
            return self.get()
