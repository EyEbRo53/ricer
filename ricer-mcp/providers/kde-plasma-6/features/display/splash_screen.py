"""Feature: Splash Screen (theme and enable/disable)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class SplashScreenFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, theme: str = None, enabled: bool = None) -> bool:
        success = True
        if theme is not None:
            success = write_kde_config("ksplashrc", "KSplash", "Theme", theme) and success
        if enabled is not None:
            value = "true" if enabled else "false"
            success = write_kde_config("ksplashrc", "KSplash", "Enabled", value) and success
        return success

    def get(self) -> dict:
        theme = read_kde_config("ksplashrc", "KSplash", "Theme", "")
        enabled = read_kde_config("ksplashrc", "KSplash", "Enabled", "true")
        return {
            "setting": "splash_screen",
            "file": "ksplashrc",
            "group": "KSplash",
            "theme": theme,
            "enabled": enabled == "true",
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_splash_screen(theme: str = None, enabled: bool = None) -> str:
            import json
            receipt = changeset.add(
                "splash_screen", {"theme": theme, "enabled": enabled}
            )
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_splash_screen() -> dict:
            return self.get()
