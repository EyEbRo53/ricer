"""Feature: task switcher (workspace)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs

from feature import FeatureType

class TaskSwitcherFeature(Feature):
    type = FeatureType.WORKSPACE
    """Task switcher feature implementation."""

    def set(self, layout_name: str = None, show_desktop: bool = None) -> bool:
        """Configure the alt-tab task switcher style."""
        configs = []
        if layout_name is not None:
            configs.append(("kwinrc", "TabBox", "LayoutName", layout_name))
        
        if show_desktop is not None:
            configs.append(("kwinrc", "TabBox", "ShowDesktop", str(show_desktop).lower()))

        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current task switcher settings."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "task_switcher",
            "values": {
                "layout_name": read_kde_config("kwinrc", "TabBox", "LayoutName", "breeze"),
                "show_desktop": read_kde_config("kwinrc", "TabBox", "ShowDesktop", "false") == "true",
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_task_switcher(
            layout_name: str = None, show_desktop: bool = None
        ) -> str:
            """Stage task switcher settings (Alt+Tab style)."""
            import json

            parameters = {k: v for k, v in {"layout_name": layout_name, "show_desktop": show_desktop}.items() if v is not None}

            receipt = changeset.add(
                description=(
                    f"Set task switcher: {', '.join(f'{k}={v}' for k, v in parameters.items())}"
                ),
                change_type="workspace",
                script="set_task_switcher",
                parameters=parameters,
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://workspace/task-switcher")
        def get_task_switcher_resource() -> str:
            """Return current task switcher settings."""
            import json

            return json.dumps(feature.get(), indent=2)


feature = TaskSwitcherFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
