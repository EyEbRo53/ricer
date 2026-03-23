"""Feature: Window Rules (arbitrary KWin window rules)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class WindowRuleFeature(Feature):
    type = FeatureType.DISPLAY

    def set(self, rule_number: int, description: str = None, windowtypes: str = None, wmclass: str = None, desktop: int = None, desktoprule: int = None) -> bool:
        # Each kwin rule is a group in kwinrulesrc, e.g. [1], [2], ...
        success = True
        if description is not None:
            success = write_kde_config("kwinrulesrc", str(rule_number), "Description", description) and success
        if windowtypes is not None:
            success = write_kde_config("kwinrulesrc", str(rule_number), "windowtypes", windowtypes) and success
        if wmclass is not None:
            success = write_kde_config("kwinrulesrc", str(rule_number), "wmclass", wmclass) and success
        if desktop is not None:
            success = write_kde_config("kwinrulesrc", str(rule_number), "desktop", str(desktop)) and success
        if desktoprule is not None:
            success = write_kde_config("kwinrulesrc", str(rule_number), "desktoprule", str(desktoprule)) and success
        return success

    def get(self, rule_number: int) -> dict:
        description = read_kde_config("kwinrulesrc", str(rule_number), "Description", "")
        windowtypes = read_kde_config("kwinrulesrc", str(rule_number), "windowtypes", "")
        wmclass = read_kde_config("kwinrulesrc", str(rule_number), "wmclass", "")
        desktop = read_kde_config("kwinrulesrc", str(rule_number), "desktop", "")
        desktoprule = read_kde_config("kwinrulesrc", str(rule_number), "desktoprule", "")
        return {
            "setting": "window_rule",
            "file": "kwinrulesrc",
            "group": str(rule_number),
            "description": description,
            "windowtypes": windowtypes,
            "wmclass": wmclass,
            "desktop": desktop,
            "desktoprule": desktoprule,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_window_rule(rule_number: int, description: str = None, windowtypes: str = None, wmclass: str = None, desktop: int = None, desktoprule: int = None) -> str:
            import json
            receipt = changeset.add(
                "window_rule", {
                    "rule_number": rule_number,
                    "description": description,
                    "windowtypes": windowtypes,
                    "wmclass": wmclass,
                    "desktop": desktop,
                    "desktoprule": desktoprule,
                }
            )
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_window_rule(rule_number: int) -> dict:
            return self.get(rule_number)
