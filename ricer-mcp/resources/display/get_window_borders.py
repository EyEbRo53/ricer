"""Resource: current window border settings (display — reads from kwinrc)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


def register(mcp):
    @mcp.resource("plasma://display/window-borders")
    def get_window_borders() -> str:
        """Return the current window border size and snap zone.

        Reads [org.kde.kdecoration2] BorderSize and [Windows] BorderSnapZone
        from kwinrc via kreadconfig6.

        Corresponds to tool: set_window_borders
        """
        import json
        from utilities.kde_config_reader import read_kde_config

        border_size = read_kde_config(
            "kwinrc", "org.kde.kdecoration2", "BorderSize", "Normal"
        )
        snap_zone = read_kde_config("kwinrc", "Windows", "BorderSnapZone", "10")

        return json.dumps(
            {
                "setting": "window_borders",
                "file": "kwinrc",
                "values": {
                    "border_size": border_size,
                    "snap_zone": (
                        int(snap_zone) if snap_zone and snap_zone.isdigit() else snap_zone
                    ),
                },
            },
            indent=2,
        )
