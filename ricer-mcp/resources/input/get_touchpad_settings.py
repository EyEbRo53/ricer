"""Resource: current touchpad settings (input — reads from kcminputrc)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


def register(mcp):
    @mcp.resource("plasma://input/touchpad-settings")
    def get_touchpad_settings() -> str:
        """Return current touchpad acceleration, speed, and deceleration.

        Reads [Touchpad] Acceleration / Speed / Deceleration from kcminputrc
        via kreadconfig6.

        Corresponds to tool: set_touchpad_settings
        """
        import json
        from utilities.kde_config_reader import read_kde_configs

        configs = [
            ("kcminputrc", "Touchpad", "Acceleration", "0"),
            ("kcminputrc", "Touchpad", "Speed", "0"),
            ("kcminputrc", "Touchpad", "Deceleration", "0"),
        ]
        values = read_kde_configs(configs)

        def _float_or_raw(v):
            try:
                return float(v) if v else v
            except (ValueError, TypeError):
                return v

        return json.dumps(
            {
                "setting": "touchpad_settings",
                "file": "kcminputrc",
                "group": "Touchpad",
                "values": {
                    "acceleration": _float_or_raw(values.get("Acceleration")),
                    "speed": _float_or_raw(values.get("Speed")),
                    "deceleration": _float_or_raw(values.get("Deceleration")),
                },
            },
            indent=2,
        )
