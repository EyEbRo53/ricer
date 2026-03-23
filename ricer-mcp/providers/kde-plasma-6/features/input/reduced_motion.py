"""Feature: Reduced Motion accessibility (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
from utils.reload.reconfigure_kwin import reconfigure_kwin

class ReducedMotionFeature(Feature):
    type = FeatureType.INPUT

    def set(self, minimal: bool = False) -> bool:
        speed = "1" if minimal else "0"
        success = write_kde_config("kwinrc", "Compositing", "AnimationSpeed", speed)
        if success:
            reconfigure_kwin()
        return success

    def get(self) -> dict:
        value = read_kde_config("kwinrc", "Compositing", "AnimationSpeed", "0")
        return {
            "setting": "reduced_motion",
            "file": "kwinrc",
            "group": "Compositing",
            "key": "AnimationSpeed",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_reduced_motion(minimal: bool = False) -> str:
            import json
            receipt = changeset.add("reduced_motion", {"minimal": minimal})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_reduced_motion() -> dict:
            return self.get()
