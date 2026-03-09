"""Resource: current double-click interval (input — reads from kdeglobals)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


def register(mcp):
    @mcp.resource("plasma://input/double-click-interval")
    def get_double_click_interval() -> str:
        """Return the current double-click interval in milliseconds.

        Reads [KDE] DoubleClickInterval from kdeglobals via kreadconfig6.

        Corresponds to tool: set_double_click_interval
        """
        import json
        from utilities.kde_config_reader import read_kde_config

        value = read_kde_config("kdeglobals", "KDE", "DoubleClickInterval", "400")
        return json.dumps(
            {
                "setting": "double_click_interval",
                "file": "kdeglobals",
                "group": "KDE",
                "key": "DoubleClickInterval",
                "value": int(value) if value and value.isdigit() else value,
                "unit": "ms",
            },
            indent=2,
        )
