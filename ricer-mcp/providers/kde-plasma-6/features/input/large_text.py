"""Feature: Large Text accessibility (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class LargeTextFeature(Feature):
    type = FeatureType.INPUT

    def set(self, font: str) -> bool:
        # font string should be in the format: "FontName,Size,Weight,Style"
        return write_kde_config("kdeglobals", "General", "font", font)

    def get(self) -> dict:
        value = read_kde_config("kdeglobals", "General", "font", "")
        return {
            "setting": "large_text",
            "file": "kdeglobals",
            "group": "General",
            "key": "font",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_large_text(font: str) -> str:
            """Stage current large text setting."""
            import json
            receipt = changeset.add("large_text", {"font": font})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_large_text() -> dict:
            """Return current large text setting."""
            return self.get()
