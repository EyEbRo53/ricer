"""Feature: screen edges (workspace)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs

from feature import FeatureType

class ScreenEdgesFeature(Feature):
    type = FeatureType.WORKSPACE
    """Screen edges feature implementation."""

    def set(
        self, 
        enabled: bool = None, 
        touch_enabled: bool = None, 
        electric_left: int = None,
        electric_right: int = None,
        electric_top: int = None,
        electric_bottom: int = None,
    ) -> bool:
        """Configure KDE screen edges (electric borders)."""
        configs = []
        if enabled is not None:
            configs.append(("kwinrc", "ScreenEdges", "ElectricBordersEnabled", str(enabled).lower()))
        if touch_enabled is not None:
            configs.append(("kwinrc", "ScreenEdges", "TouchScreenEdgesEnabled", str(touch_enabled).lower()))
            
        if electric_left is not None:
            configs.append(("kwinrc", "ScreenEdges", "ElectricLeft", str(electric_left)))
        if electric_right is not None:
            configs.append(("kwinrc", "ScreenEdges", "ElectricRight", str(electric_right)))
        if electric_top is not None:
            configs.append(("kwinrc", "ScreenEdges", "ElectricTop", str(electric_top)))
        if electric_bottom is not None:
            configs.append(("kwinrc", "ScreenEdges", "ElectricBottom", str(electric_bottom)))

        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current screen edges settings."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "screen_edges",
            "values": {
                "enabled": read_kde_config("kwinrc", "ScreenEdges", "ElectricBordersEnabled", "true") == "true",
                "touch_enabled": read_kde_config("kwinrc", "ScreenEdges", "TouchScreenEdgesEnabled", "true") == "true",
                "electric_left": read_kde_config("kwinrc", "ScreenEdges", "ElectricLeft", "0"),
                "electric_right": read_kde_config("kwinrc", "ScreenEdges", "ElectricRight", "0"),
                "electric_top": read_kde_config("kwinrc", "ScreenEdges", "ElectricTop", "0"),
                "electric_bottom": read_kde_config("kwinrc", "ScreenEdges", "ElectricBottom", "0"),
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_screen_edges(
            enabled: bool = None, 
            touch_enabled: bool = None, 
            electric_left: int = None,
            electric_right: int = None,
            electric_top: int = None,
            electric_bottom: int = None,
        ) -> str:
            """Stage screen edges (electric borders) settings."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set screen edges: enabled={enabled}, left={electric_left}, etc."
                ),
                change_type="workspace",
                script="set_screen_edges",
                parameters={
                    "enabled": enabled,
                    "touch_enabled": touch_enabled,
                    "electric_left": electric_left,
                    "electric_right": electric_right,
                    "electric_top": electric_top,
                    "electric_bottom": electric_bottom,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://workspace/screen-edges")
        def get_screen_edges_resource() -> str:
            """Return current screen edges settings."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = ScreenEdgesFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
