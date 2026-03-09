"""Resource: current cursor size (input — reads from kcminputrc)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


def register(mcp):
    @mcp.resource("plasma://input/cursor-size")
    def get_cursor_size() -> str:
        """Return the current cursor size in pixels.

        Reads [Mouse] cursorSize from kcminputrc via kreadconfig6.

        Corresponds to tool: set_cursor_size
        """
        import json
        from utilities.kde_config_reader import read_kde_config

        value = read_kde_config("kcminputrc", "Mouse", "cursorSize", "24")
        return json.dumps(
            {
                "setting": "cursor_size",
                "file": "kcminputrc",
                "group": "Mouse",
                "key": "cursorSize",
                "value": int(value) if value and value.isdigit() else value,
                "unit": "px",
            },
            indent=2,
        )
