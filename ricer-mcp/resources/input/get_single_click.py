"""Resource: current single-click mode (input — reads from kdeglobals)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


def register(mcp):
    @mcp.resource("plasma://input/single-click")
    def get_single_click() -> str:
        """Return whether single-click to open is enabled.

        Reads [KDE] SingleClick from kdeglobals via kreadconfig6.

        Corresponds to tool: set_single_click
        """
        import json
        from utilities.kde_config_reader import read_kde_config

        value = read_kde_config("kdeglobals", "KDE", "SingleClick", "true")
        return json.dumps(
            {
                "setting": "single_click",
                "file": "kdeglobals",
                "group": "KDE",
                "key": "SingleClick",
                "value": value,
                "enabled": value.lower() == "true" if value else None,
            },
            indent=2,
        )
