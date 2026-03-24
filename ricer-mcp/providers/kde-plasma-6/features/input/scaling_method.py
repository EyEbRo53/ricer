"""Feature: scaling method (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
from utils.reload.reconfigure_kwin import reconfigure_kwin

class ScalingMethodFeature(Feature):
    type = FeatureType.INPUT

    def set(self, method: str) -> bool:
        success = write_kde_config("kwinrc", "Compositing", "ScaleMethod", method)
        if success:
            reconfigure_kwin()
        return success

    def get(self) -> dict:
        value = read_kde_config("kwinrc", "Compositing", "ScaleMethod", "Smooth")
        return {
            "setting": "scaling_method",
            "file": "kwinrc",
            "group": "Compositing",
            "key": "ScaleMethod",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_scaling_method(method: str) -> str:
            """Stage current scaling method setting."""
            import json
            receipt = changeset.add("scaling_method", {"method": method})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_scaling_method() -> dict:
            """Return current scaling method setting."""
            return self.get()
