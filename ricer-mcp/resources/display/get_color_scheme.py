"""Resource: current color scheme (display — reads from kdeglobals)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


def register(mcp):
    @mcp.resource("plasma://display/color-scheme")
    def get_color_scheme() -> str:
        """Return the current active color scheme.

        Reads [General] ColorScheme from kdeglobals via kreadconfig6.

        Corresponds to tool: set_color_scheme
        """
        import json
        from utilities.kde_config_reader import read_kde_config

        value = read_kde_config("kdeglobals", "General", "ColorScheme", "Breeze")
        return json.dumps(
            {
                "setting": "color_scheme",
                "file": "kdeglobals",
                "group": "General",
                "key": "ColorScheme",
                "value": value,
                "description": "Current color scheme/theme used by KDE Plasma",
            },
            indent=2,
        )
