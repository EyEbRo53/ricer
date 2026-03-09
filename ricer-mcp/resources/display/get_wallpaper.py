"""Resource: current wallpaper (display — reads via DBus)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


def register(mcp):
    @mcp.resource("plasma://display/wallpaper")
    def get_wallpaper() -> str:
        """Return the current desktop wallpaper path.

        Queries the Plasma shell via DBus to get the active wallpaper image.

        Corresponds to tool: change_wallpaper
        """
        import json
        from utilities.kde_config_reader import read_current_wallpaper

        path = read_current_wallpaper()
        return json.dumps(
            {
                "setting": "wallpaper",
                "source": "dbus (org.kde.plasmashell)",
                "value": path,
            },
            indent=2,
        )
