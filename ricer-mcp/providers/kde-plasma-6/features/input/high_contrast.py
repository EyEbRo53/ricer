"""Feature: High Contrast accessibility (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
import os

class HighContrastFeature(Feature):
    type = FeatureType.INPUT

    def set(self, enable: bool) -> bool:
        # Set color scheme
        color_scheme_success = write_kde_config("kdeglobals", "General", "ColorScheme", "HighContrast" if enable else "BreezeLight")
        # Set Trolltech.conf for QT apps
        trolltech_conf = os.path.expanduser("~/.config/Trolltech.conf")
        qt_style_success = write_kde_config(trolltech_conf, "Qt", "style", "fusion" if enable else "")
        return color_scheme_success and qt_style_success

    def get(self) -> dict:
        color_scheme = read_kde_config("kdeglobals", "General", "ColorScheme", "BreezeLight")
        trolltech_conf = os.path.expanduser("~/.config/Trolltech.conf")
        qt_style = read_kde_config(trolltech_conf, "Qt", "style", "")
        return {
            "setting": "high_contrast",
            "color_scheme": color_scheme,
            "qt_style": qt_style,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_high_contrast(enable: bool) -> str:
            """Stage current high contrast setting."""
            import json
            receipt = changeset.add("high_contrast", {"enable": enable})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_high_contrast() -> dict:
            """Return current high contrast setting."""
            return self.get()
