"""Feature: double-click interval (input)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_config


class DoubleClickIntervalFeature(Feature):
    """Double-click interval feature implementation."""

    def execute(self, interval: int) -> bool:
        """Configure double-click interval via orchestrator."""
        return write_kde_config("kdeglobals", "KDE", "DoubleClickInterval", str(interval))

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
        def get_double_click_interval() -> str:
            """Return the current double-click interval in milliseconds."""
            import json
            from utils.kde_config_reader import read_kde_config

            value = read_kde_config("kdeglobals", "KDE", "DoubleClickInterval", "400")
            parsed_value = int(value) if value and value.isdigit() else value
            return json.dumps(
                {
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
                },
                indent=2,
            )


feature = DoubleClickIntervalFeature()


def set_double_click_interval(interval: int) -> bool:
    """Script entrypoint for confirmed double-click interval changes."""
    return feature.execute(interval=interval)


def register(mcp, changeset):
    feature.register(mcp, changeset)
