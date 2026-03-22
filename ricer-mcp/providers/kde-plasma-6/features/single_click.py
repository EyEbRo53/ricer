"""Feature: single-click mode (input)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_config


class SingleClickFeature(Feature):
    """Single-click feature implementation."""

    def set(self, enabled: bool) -> bool:
        """Configure single-click to open via orchestrator."""
        value = "true" if enabled else "false"
        return write_kde_config("kdeglobals", "KDE", "SingleClick", value)

    def get(self) -> dict:
        """Return current single-click state as a structured payload."""
        from utils.kde_config_reader import read_kde_config

        value = read_kde_config("kdeglobals", "KDE", "SingleClick", "true")
        return {
            "setting": "single_click",
            "file": "kdeglobals",
            "group": "KDE",
            "key": "SingleClick",
            "value": value,
            "enabled": value.lower() == "true" if value else None,
            "error": (
                "Failed to read kdeglobals [KDE] SingleClick via kreadconfig6."
                if value is None
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_single_click(enabled: bool) -> str:
            """Stage a single-click to open files/folders change."""
            import json

            state = "enabled" if enabled else "disabled"
            receipt = changeset.add(
                description=f"Set single-click to open: {state}",
                change_type="input",
                script="set_single_click",
                parameters={"enabled": enabled},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://input/single-click")
        def get_single_click_resource() -> str:
            """Return whether single-click to open is enabled."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = SingleClickFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
