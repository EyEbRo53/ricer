"""Feature: animation speed (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class AnimationSpeedFeature(Feature):
    type = FeatureType.INPUT

    def set(self, speed: int) -> bool:
        """Set KDE Plasma animation speed via kwriteconfig6."""
        return write_kde_config("kwinrc", "Compositing", "AnimationSpeed", str(speed))

    def get(self) -> dict:
        """Return current animation speed as a structured payload."""
        value = read_kde_config("kwinrc", "Compositing", "AnimationSpeed", "4")
        return {
            "setting": "animation_speed",
            "file": "kwinrc",
            "group": "Compositing",
            "key": "AnimationSpeed",
            "value": int(value) if value and value.isdigit() else value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_animation_speed(speed: int) -> str:
            """Stage an animation speed change."""
            import json
            receipt = changeset.add("animation_speed", {"speed": speed})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_animation_speed() -> dict:
            """Return current animation speed setting."""
            return self.get()
