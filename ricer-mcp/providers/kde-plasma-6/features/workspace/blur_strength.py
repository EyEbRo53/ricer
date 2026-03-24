"""Feature: blur strength (workspace/desktop effects)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_config

from feature import FeatureType

class BlurStrengthFeature(Feature):
    type = FeatureType.WORKSPACE
    """Blur strength feature implementation."""

    def set(self, strength: int) -> bool:
        """Configure KWin blur effect strength (typically 1-10)."""
        return write_kde_config("kwinrc", "Plugins", "kwin4_effect_blurStrength", str(strength))

    def get(self) -> dict:
        """Return current blur strength setting."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "blur_strength",
            "values": {
                "strength": read_kde_config("kwinrc", "Plugins", "kwin4_effect_blurStrength", "5"),
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_blur_strength(strength: int) -> str:
            """Stage KWin blur strength setting (1-10)."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set blur strength to {strength}"
                ),
                change_type="workspace",
                script="set_blur_strength",
                parameters={
                    "strength": strength,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://workspace/blur-strength")
        def get_blur_strength_resource() -> str:
            """Return current blur strength setting."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = BlurStrengthFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
