"""Feature: Window rules (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
from utils.reload.reconfigure_kwin import reconfigure_kwin
import os

class WindowRuleFeature(Feature):
    type = FeatureType.INPUT

    def set(self, rule_number: int, description: str, window_type: str, wmclass: str, desktop: int, desktoprule: int) -> bool:
        config_file = os.path.expanduser("~/.config/kwinrulesrc")
        group = str(rule_number)
        success = True
        success &= write_kde_config(config_file, group, "Description", description)
        success &= write_kde_config(config_file, group, "windowtypes", window_type)
        success &= write_kde_config(config_file, group, "wmclass", wmclass)
        success &= write_kde_config(config_file, group, "desktop", str(desktop))
        success &= write_kde_config(config_file, group, "desktoprule", str(desktoprule))
        if success:
            reconfigure_kwin()
        return success

    def get(self, rule_number: int) -> dict:
        config_file = os.path.expanduser("~/.config/kwinrulesrc")
        group = str(rule_number)
        description = read_kde_config(config_file, group, "Description", "")
        window_type = read_kde_config(config_file, group, "windowtypes", "")
        wmclass = read_kde_config(config_file, group, "wmclass", "")
        desktop = read_kde_config(config_file, group, "desktop", "")
        desktoprule = read_kde_config(config_file, group, "desktoprule", "")
        return {
            "setting": "window_rule",
            "rule_number": rule_number,
            "description": description,
            "window_type": window_type,
            "wmclass": wmclass,
            "desktop": desktop,
            "desktoprule": desktoprule,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_window_rule(rule_number: int, description: str, window_type: str, wmclass: str, desktop: int, desktoprule: int) -> str:
            """Stage current window rule setting."""
            import json
            receipt = changeset.add("window_rule", {
                "rule_number": rule_number,
                "description": description,
                "window_type": window_type,
                "wmclass": wmclass,
                "desktop": desktop,
                "desktoprule": desktoprule
            })
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_window_rule(rule_number: int) -> dict:
            """Return current window rule setting."""
            return self.get(rule_number)
