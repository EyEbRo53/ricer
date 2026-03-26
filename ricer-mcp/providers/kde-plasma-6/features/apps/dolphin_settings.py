"""Feature: dolphin settings (apps)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs

from feature import FeatureType

class DolphinSettingsFeature(Feature):
    type = FeatureType.APPS
    """Dolphin file manager feature implementation."""

    def set(
        self,
        view_mode: int = None,
        show_hidden_files: bool = None,
        sorting: str = None,
        sorting_order: int = None,
        show_folder_previews: bool = None,
    ) -> bool:
        """Configure Dolphin File Manager settings."""
        configs = []
        if view_mode is not None:
            configs.append(("dolphinrc", "General", "View Mode", str(view_mode)))
        if show_hidden_files is not None:
            configs.append(("dolphinrc", "General", "Show Hidden Files", str(show_hidden_files).lower()))
        if sorting is not None:
            configs.append(("dolphinrc", "General", "Sorting", sorting))
        if sorting_order is not None:
            configs.append(("dolphinrc", "General", "SortingOrder", str(sorting_order)))
        if show_folder_previews is not None:
            configs.append(("dolphinrc", "General", "Show Folder Previews", str(show_folder_previews).lower()))

        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current Dolphin settings."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "dolphin_settings",
            "values": {
                "view_mode": read_kde_config("dolphinrc", "General", "View Mode", "0"),
                "show_hidden_files": read_kde_config("dolphinrc", "General", "Show Hidden Files", "false") == "true",
                "sorting": read_kde_config("dolphinrc", "General", "Sorting", "Name"),
                "sorting_order": read_kde_config("dolphinrc", "General", "SortingOrder", "0"),
                "show_folder_previews": read_kde_config("dolphinrc", "General", "Show Folder Previews", "true") == "true",
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_dolphin_settings(
            view_mode: int = None,
            show_hidden_files: bool = None,
            sorting: str = None,
            sorting_order: int = None,
            show_folder_previews: bool = None,
        ) -> str:
            """Stage Dolphin file manager settings."""
            import json

            parameters = {k: v for k, v in {
                "view_mode": view_mode,
                "show_hidden_files": show_hidden_files,
                "sorting": sorting,
                "sorting_order": sorting_order,
                "show_folder_previews": show_folder_previews,
            }.items() if v is not None}

            receipt = changeset.add(
                description=(
                    f"Set Dolphin settings: {', '.join(f'{k}={v}' for k, v in parameters.items())}"
                ),
                change_type="apps",
                script="set_dolphin_settings",
                parameters=parameters,
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://apps/dolphin-settings")
        def get_dolphin_settings_resource() -> str:
            """Return current Dolphin file manager settings."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = DolphinSettingsFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
