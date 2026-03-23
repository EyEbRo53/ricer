"""Feature: window borders (display)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs


from feature import FeatureType

class WindowBordersFeature(Feature):
    type = FeatureType.DISPLAY
    """Window borders feature implementation."""

    def set(self, border_size: str, snap_zone: int) -> bool:
        """Configure titlebars, window borders and snap zones."""
        configs = [
            ("kwinrc", "org.kde.kdecoration2", "BorderSize", str(border_size)),
            ("kwinrc", "Windows", "BorderSnapZone", str(snap_zone)),
        ]
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current window border settings as a structured payload."""
        from utils.kde_config_reader import read_kde_config

        border_size = read_kde_config(
            "kwinrc", "org.kde.kdecoration2", "BorderSize", "Normal"
        )
        snap_zone = read_kde_config("kwinrc", "Windows", "BorderSnapZone", "10")
        failed_keys = []
        if border_size is None:
            failed_keys.append("org.kde.kdecoration2/BorderSize")
        if snap_zone is None:
            failed_keys.append("Windows/BorderSnapZone")

        return {
            "setting": "window_borders",
            "file": "kwinrc",
            "values": {
                "border_size": border_size,
                "snap_zone": (
                    int(snap_zone) if snap_zone and str(snap_zone).isdigit() else snap_zone
                ),
            },
            "error": (
                "Failed to read kwinrc keys via kreadconfig6: "
                + ", ".join(failed_keys)
                if failed_keys
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_window_borders(border_size: str, snap_zone: int) -> str:
            """Stage a window border size and snap zone change."""
            import json

            receipt = changeset.add(
                description=f"Set window borders to {border_size} with snap zone {snap_zone}px",
                change_type="display",
                script="set_window_borders",
                parameters={"border_size": border_size, "snap_zone": snap_zone},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://display/window-borders")
        def get_window_borders_resource() -> str:
            """Return the current window border size and snap zone."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = WindowBordersFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
