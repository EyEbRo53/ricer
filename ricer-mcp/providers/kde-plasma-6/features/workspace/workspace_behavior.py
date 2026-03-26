"""Feature: workspace behavior (workspace)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs

from feature import FeatureType

class WorkspaceBehaviorFeature(Feature):
    type = FeatureType.WORKSPACE
    """Workspace behavior feature implementation."""

    def set(self, tool_button_style: str = None, scrollbar_click_behavior: str = None) -> bool:
        """Configure general workspace behaviors like tool button styles and scrollbar clicks."""
        configs = []
        if tool_button_style is not None:
            configs.append(("kdeglobals", "KDE", "ToolButtonStyle", tool_button_style))
        if scrollbar_click_behavior is not None:
            configs.append(("kdeglobals", "KDE", "ScrollBarClickBehavior", scrollbar_click_behavior))

        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current workspace behavior settings."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "workspace_behavior",
            "values": {
                "tool_button_style": read_kde_config("kdeglobals", "KDE", "ToolButtonStyle", "TextBesideIcon"),
                "scrollbar_click_behavior": read_kde_config("kdeglobals", "KDE", "ScrollBarClickBehavior", "JumpToPos"),
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_workspace_behavior(
            tool_button_style: str = None, scrollbar_click_behavior: str = None
        ) -> str:
            """Stage general workspace behavior settings."""
            import json

            parameters = {k: v for k, v in {"tool_button_style": tool_button_style, "scrollbar_click_behavior": scrollbar_click_behavior}.items() if v is not None}

            receipt = changeset.add(
                description=(
                    f"Set workspace behavior: {', '.join(f'{k}={v}' for k, v in parameters.items())}"
                ),
                change_type="workspace",
                script="set_workspace_behavior",
                parameters=parameters,
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://workspace/workspace-behavior")
        def get_workspace_behavior_resource() -> str:
            """Return current workspace behavior settings."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = WorkspaceBehaviorFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
