"""Feature: window snapping (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
from utils.reload.reconfigure_kwin import reconfigure_kwin

class WindowSnappingFeature(Feature):
    type = FeatureType.INPUT

    def set(self, enabled: bool) -> bool:
        value = "true" if enabled else "false"
        success = write_kde_config("kwinrc", "Windows", "SnapOnlyWhenOverlapping", value)
        if success:
            reconfigure_kwin()
        return success

    def get(self) -> dict:
        value = read_kde_config("kwinrc", "Windows", "SnapOnlyWhenOverlapping", "true")
        return {
            "setting": "window_snapping",
            "file": "kwinrc",
            "group": "Windows",
            "key": "SnapOnlyWhenOverlapping",
            "value": value,
            "enabled": value == "true",
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_window_snapping(enabled: bool) -> str:
            """Stage current window snapping setting."""
            import json
            receipt = changeset.add("window_snapping", {"enabled": enabled})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_window_snapping() -> dict:
            """Return current window snapping setting."""
            return self.get()
