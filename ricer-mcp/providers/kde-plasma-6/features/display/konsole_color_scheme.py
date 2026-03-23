"""Feature: Konsole color scheme (display)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
import os

class KonsoleColorSchemeFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, profile_name: str, color_scheme: str) -> bool:
        profile_file = os.path.expanduser(f"~/.local/share/konsole/{profile_name}.profile")
        return write_kde_config(profile_file, "Appearance", "ColorScheme", color_scheme)

    def get(self, profile_name: str) -> dict:
        profile_file = os.path.expanduser(f"~/.local/share/konsole/{profile_name}.profile")
        value = read_kde_config(profile_file, "Appearance", "ColorScheme", "")
        return {
            "setting": "konsole_color_scheme",
            "profile_name": profile_name,
            "file": profile_file,
            "group": "Appearance",
            "key": "ColorScheme",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_konsole_color_scheme(profile_name: str, color_scheme: str) -> str:
            import json
            receipt = changeset.add("konsole_color_scheme", {"profile_name": profile_name, "color_scheme": color_scheme})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_konsole_color_scheme(profile_name: str) -> dict:
            return self.get(profile_name)
