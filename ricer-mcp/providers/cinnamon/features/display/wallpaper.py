"""Feature: wallpaper (display)."""

import os
from feature import Feature, FeatureType


class WallpaperFeature(Feature):
    """Wallpaper feature implementation for Cinnamon."""
    type = FeatureType.DISPLAY

    def set(self, path: str) -> bool:
        """Set Cinnamon wallpaper via gsettings."""
        from utils.write.gsettings_writer import write_gsetting

        uri = path if path.startswith("file://") else f"file://{path}"
        return write_gsetting(
            "org.cinnamon.desktop.background", "picture-uri", f"'{uri}'"
        )

    def get(self) -> dict:
        """Return current wallpaper as structured payload."""
        from utils.read.gsettings_reader import read_gsetting

        value = read_gsetting("org.cinnamon.desktop.background", "picture-uri")
        # Strip the file:// prefix for display
        display_path = value
        if value and value.startswith("file://"):
            display_path = value[7:]
        return {
            "setting": "wallpaper",
            "source": "gsettings (org.cinnamon.desktop.background)",
            "value": display_path,
            "raw_uri": value,
            "error": (
                "Failed to read wallpaper from gsettings."
                if value is None
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_wallpaper(path: str) -> str:
            """Stage a wallpaper change.

            Args:
                path: Absolute path to the wallpaper image file.

            Returns:
                JSON staging receipt with order number, script, and parameters.
            """
            import json

            filename = os.path.basename(path)
            receipt = changeset.add(
                description=f"Change wallpaper to {filename}",
                change_type="display",
                script="set_wallpaper",
                parameters={"path": path},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("cinnamon://display/wallpaper")
        def get_wallpaper_resource() -> str:
            """Return the current desktop wallpaper path."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = WallpaperFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
