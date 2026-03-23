"""Feature: double-click interval (input)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_config


from feature import FeatureType

class DoubleClickIntervalFeature(Feature):
    type = FeatureType.INPUT
    """Double-click interval feature implementation."""

    def set(self, interval: int) -> bool:
        """Configure double-click interval via orchestrator."""
        return write_kde_config("kdeglobals", "KDE", "DoubleClickInterval", str(interval))

    def get(self) -> dict:
        """Return the current double-click interval as a structured payload."""
        from utils.kde_config_reader import read_kde_config

        value = read_kde_config("kdeglobals", "KDE", "DoubleClickInterval", "400")
        parsed_value = int(value) if value and str(value).isdigit() else value
        return {
            "setting": "double_click_interval",
            "file": "kdeglobals",
            "group": "KDE",
            "key": "DoubleClickInterval",
            "value": parsed_value,
            "unit": "ms",
            "error": (
                "Failed to read kdeglobals [KDE] DoubleClickInterval via kreadconfig6."
                if value is None
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_double_click_interval(interval: int) -> str:
            """Stage a double-click interval change."""
            import json

            receipt = changeset.add(
                description=f"Set double-click interval to {interval}ms",
                change_type="input",
                script="set_double_click_interval",
                parameters={"interval": interval},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://input/double-click-interval")
        def get_double_click_interval_resource() -> str:
            """Return the current double-click interval in milliseconds."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = DoubleClickIntervalFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
