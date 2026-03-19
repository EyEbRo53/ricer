"""Feature: wallpaper (display)."""

import os
from feature import Feature
from utils.write.plasma_script import run_plasma_script


class WallpaperFeature(Feature):
    """Wallpaper feature implementation."""

    def execute(self, path: str) -> bool:
        """Set KDE Plasma wallpaper via orchestrator."""
        script = f"""
    var allDesktops = desktops();
    for (i=0; i<allDesktops.length; i++) {{
        d = allDesktops[i];
        d.wallpaperPlugin = \"org.kde.image\";
        d.currentConfigGroup = [\"Wallpaper\", \"org.kde.image\", \"General\"];
        d.writeConfig(\"Image\", \"file://{path}\");
    }}
    """
        return run_plasma_script(script, f"Wallpaper set: {os.path.basename(path)}")

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_wallpaper(path: str) -> str:
            """Stage a wallpaper change."""
            import json
            import os

            filename = os.path.basename(path)
            receipt = changeset.add(
                description=f"Change wallpaper to {filename}",
                change_type="display",
                script="set_wallpaper",
                parameters={"path": path},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://display/wallpaper")
        def get_wallpaper() -> str:
            """Return the current desktop wallpaper path."""
            import json
            from utils.kde_config_reader import read_current_wallpaper

            path = read_current_wallpaper()
            return json.dumps(
                {
                    "setting": "wallpaper",
                    "source": "dbus (org.kde.plasmashell)",
                    "value": path,
                    "error": (
                        "Failed to read wallpaper from DBus (org.kde.plasmashell)."
                        if path is None
                        else None
                    ),
                },
                indent=2,
            )


feature = WallpaperFeature()


def set_wallpaper(path: str) -> bool:
    """Script entrypoint for confirmed wallpaper changes."""
    return feature.execute(path=path)


def register(mcp, changeset):
    feature.register(mcp, changeset)
