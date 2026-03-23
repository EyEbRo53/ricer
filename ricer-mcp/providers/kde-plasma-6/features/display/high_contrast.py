"""Feature: High Contrast Accessibility (color scheme and Trolltech.conf)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
import os

class HighContrastFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, enable: bool = True) -> bool:
        # Set KDE color scheme to HighContrast
        color_scheme_success = write_kde_config("kdeglobals", "General", "ColorScheme", "HighContrast") if enable else True
        # Set Trolltech.conf style to fusion for high contrast in Qt apps
        trolltech_conf = os.path.expanduser("~/.config/Trolltech.conf")
        trolltech_success = write_kde_config(trolltech_conf, "Qt", "style", "fusion") if enable else True
        return color_scheme_success and trolltech_success

    def get(self) -> dict:
        color_scheme = read_kde_config("kdeglobals", "General", "ColorScheme", "")
        import os
        trolltech_conf = os.path.expanduser("~/.config/Trolltech.conf")
        qt_style = read_kde_config(trolltech_conf, "Qt", "style", "")
        return {
            "setting": "high_contrast",
            "file": ["kdeglobals", trolltech_conf],
            "color_scheme": color_scheme,
            "qt_style": qt_style,
            "enabled": color_scheme == "HighContrast" and qt_style == "fusion",
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_high_contrast(enable: bool = True) -> str:
            import json
            receipt = changeset.add("high_contrast", {"enable": enable})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_high_contrast() -> dict:
            return self.get()
