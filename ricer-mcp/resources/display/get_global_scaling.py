"""Resource: current global display scaling (display — reads via kscreen-doctor)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


def register(mcp):
    @mcp.resource("plasma://display/global-scaling")
    def get_global_scaling() -> str:
        """Return the current global UI scaling factor.

        Queries kscreen-doctor to read the active output's scale value.

        Corresponds to tool: set_global_scaling
        """
        import json
        from utilities.kde_config_reader import read_kscreen_doctor

        info = read_kscreen_doctor()
        scale = info.get("scale") if info else None
        return json.dumps(
            {
                "setting": "global_scaling",
                "source": "kscreen-doctor",
                "value": scale,
                "output": info if info else None,
            },
            indent=2,
        )
