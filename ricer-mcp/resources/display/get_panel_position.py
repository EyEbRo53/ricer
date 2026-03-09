"""Resource: current panel position (display — reads via DBus)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


def register(mcp):
    @mcp.resource("plasma://display/panel-position")
    def get_panel_position() -> str:
        """Return the current panel (taskbar) position.

        Queries the Plasma shell via DBus to get the active panel location.

        Corresponds to tool: move_panel
        """
        import json
        from utilities.kde_config_reader import read_panel_position

        position = read_panel_position()
        return json.dumps(
            {
                "setting": "panel_position",
                "source": "dbus (org.kde.plasmashell)",
                "value": position,
            },
            indent=2,
        )
