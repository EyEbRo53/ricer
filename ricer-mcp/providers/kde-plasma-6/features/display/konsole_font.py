"""Feature: Konsole font (display)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
import os

class KonsoleFontFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, profile_name: str, font: str) -> bool:
        profile_file = os.path.expanduser(f"~/.local/share/konsole/{profile_name}.profile")
        return write_kde_config(profile_file, "Appearance", "Font", font)

    def get(self, profile_name: str) -> dict:
        profile_file = os.path.expanduser(f"~/.local/share/konsole/{profile_name}.profile")
        value = read_kde_config(profile_file, "Appearance", "Font", "")
        return {
            "setting": "konsole_font",
            "profile_name": profile_name,
            "file": profile_file,
            "group": "Appearance",
            "key": "Font",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_konsole_font(profile_name: str, font: str) -> str:
            import json
            receipt = changeset.add("konsole_font", {"profile_name": profile_name, "font": font})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_konsole_font(profile_name: str) -> dict:
            return self.get(profile_name)
