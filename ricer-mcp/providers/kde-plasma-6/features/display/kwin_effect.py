"""Feature: KWin effects (enable/disable specific effects in Plugins group)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
from utils.reload.reconfigure_kwin import reconfigure_kwin

class KWinEffectFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, effect_name: str, enabled: bool) -> bool:
        value = "true" if enabled else "false"
        success = write_kde_config("kwinrc", "Plugins", f"{effect_name}Enabled", value)
        if success:
            reconfigure_kwin()
        return success

    def get(self, effect_name: str) -> dict:
        value = read_kde_config("kwinrc", "Plugins", f"{effect_name}Enabled", "false")
        return {
            "setting": "kwin_effect",
            "file": "kwinrc",
            "group": "Plugins",
            "key": f"{effect_name}Enabled",
            "value": value,
            "enabled": value == "true",
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_kwin_effect(effect_name: str, enabled: bool) -> str:
            """Stage current kwin effect setting."""
            import json
            receipt = changeset.add(
                "kwin_effect", {"effect_name": effect_name, "enabled": enabled}
            )
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_kwin_effect(effect_name: str) -> dict:
            """Return current kwin effect setting."""
            return self.get(effect_name)
