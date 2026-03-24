"""Feature: panel settings (display)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
from utils.reload.reload_plasma_shell import reload_plasma_shell

CONFIG_FILE = "plasma-org.kde.plasma.desktop-appletsrc"

class PanelFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, panel_id: int, height: int = None, visibility: str = None, location: str = None) -> bool:
        """Set panel height, visibility, or location."""
        success = True
        if height is not None:
            success &= write_kde_config(CONFIG_FILE, f"Containments-{panel_id}", "height", str(height))
        if visibility is not None:
            success &= write_kde_config(CONFIG_FILE, f"Containments-{panel_id}", "visibility", visibility)
        if location is not None:
            success &= write_kde_config(CONFIG_FILE, f"Containments-{panel_id}", "location", location)
        if success:
            reload_plasma_shell()
        return success

    def get(self, panel_id: int) -> dict:
        """Return current panel settings as a structured payload."""
        height = read_kde_config(CONFIG_FILE, f"Containments-{panel_id}", "height", "")
        visibility = read_kde_config(CONFIG_FILE, f"Containments-{panel_id}", "visibility", "")
        location = read_kde_config(CONFIG_FILE, f"Containments-{panel_id}", "location", "")
        return {
            "setting": "panel",
            "panel_id": panel_id,
            "height": height,
            "visibility": visibility,
            "location": location,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_panel(panel_id: int, height: int = None, visibility: str = None, location: str = None) -> str:
            """Stage a panel setting change."""
            import json
            receipt = changeset.add("panel", {"panel_id": panel_id, "height": height, "visibility": visibility, "location": location})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_panel(panel_id: int) -> dict:
            """Return current panel setting."""
            return self.get(panel_id)
