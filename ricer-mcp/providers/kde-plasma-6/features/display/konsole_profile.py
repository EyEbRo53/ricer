"""Feature: Konsole default profile (display)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
import os

class KonsoleProfileFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, profile_name: str) -> bool:
        return write_kde_config(os.path.expanduser("~/.config/konsolerc"), "Desktop Entry", "DefaultProfile", f"{profile_name}.profile")

    def get(self) -> dict:
        value = read_kde_config(os.path.expanduser("~/.config/konsolerc"), "Desktop Entry", "DefaultProfile", "Default.profile")
        return {
            "setting": "konsole_default_profile",
            "file": "~/.config/konsolerc",
            "group": "Desktop Entry",
            "key": "DefaultProfile",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_konsole_profile(profile_name: str) -> str:
            import json
            receipt = changeset.add("konsole_default_profile", {"profile_name": profile_name})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_konsole_profile() -> dict:
            return self.get()
