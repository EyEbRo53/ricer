"""Feature: dock (Latte Dock) settings (display)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
import os
import glob
import re
import subprocess

class DockFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, dock_name: str, dock_id: int, visibility: str) -> bool:
        """Set Latte Dock visibility mode."""
        config_file = os.path.expanduser(f"~/.config/latte/{dock_name}.layout.latte")
        group = f"Containments-{dock_id}"
        success = write_kde_config(config_file, group, "visibility", visibility)
        if success:
            subprocess.Popen(["pkill", "latte-dock"])
            subprocess.Popen(["latte-dock"])  # Restart dock
        return success

    def get(self, dock_name: str, dock_id: int) -> dict:
        config_file = os.path.expanduser(f"~/.config/latte/{dock_name}.layout.latte")
        group = f"Containments-{dock_id}"
        visibility = read_kde_config(config_file, group, "visibility", "")
        return {
            "setting": "dock",
            "dock_name": dock_name,
            "dock_id": dock_id,
            "visibility": visibility,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_dock(dock_name: str, dock_id: int, visibility: str) -> str:
            """Stage a dock visibility change."""
            import json
            receipt = changeset.add("dock", {"dock_name": dock_name, "dock_id": dock_id, "visibility": visibility})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_dock(dock_name: str, dock_id: int) -> dict:
            """Return current dock setting."""
            return self.get(dock_name, dock_id)
