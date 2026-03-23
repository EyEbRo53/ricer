"""Feature: Reduced Motion Accessibility (animation speed 0/1)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
from utils.reload.reconfigure_kwin import reconfigure_kwin

class ReducedMotionFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, minimal: bool = True) -> bool:
        # 0 = off, 1 = minimal, 4 = default
        value = "0" if minimal else "1"
        success = write_kde_config("kwinrc", "Compositing", "AnimationSpeed", value)
        if success:
            reconfigure_kwin()
        return success

    def get(self) -> dict:
        value = read_kde_config("kwinrc", "Compositing", "AnimationSpeed", "1")
        return {
            "setting": "reduced_motion",
            "file": "kwinrc",
            "group": "Compositing",
            "key": "AnimationSpeed",
            "value": value,
            "minimal": value in ("0", "1"),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_reduced_motion(minimal: bool = True) -> str:
            import json
            receipt = changeset.add("reduced_motion", {"minimal": minimal})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_reduced_motion() -> dict:
            return self.get()
