"""Feature: notifications (audio)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs, write_kde_config


from feature import FeatureType

class NotificationsFeature(Feature):
    type = FeatureType.AUDIO
    """Notifications feature implementation."""

    def set(self, enabled: bool = None, do_not_disturb: bool = None, app_name: str = None, app_settings: str = None) -> bool:
        """Configure general notification settings and app specific overrides."""
        configs = []
        if enabled is not None:
            configs.append(("plasmanotifyrc", "General", "enabled", str(enabled).lower()))
        if do_not_disturb is not None:
            configs.append(("plasmanotifyrc", "General", "show_quietly", str(do_not_disturb).lower()))
        if app_name is not None and app_settings is not None:
            configs.append(("plasmanotifyrc", "Event Settings", app_name, app_settings))
        
        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current notification settings."""
        from utils.read.kreadconfig import read_kde_configs

        configs = [
            ("plasmanotifyrc", "General", "enabled", "true"),
            ("plasmanotifyrc", "General", "show_quietly", "false"),
        ]
        values = read_kde_configs(configs)
        failed_keys = [k for k, v in values.items() if v is None]

        return {
            "setting": "notifications",
            "file": "plasmanotifyrc",
            "group": "General",
            "values": {
                "enabled": values.get("enabled") == "true",
                "do_not_disturb": values.get("show_quietly") == "true",
            },
            "error": (
                "Failed to read plasmanotifyrc notifications keys via kreadconfig6: "
                + ", ".join(failed_keys)
                if failed_keys
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_notifications(
            enabled: bool = None, do_not_disturb: bool = None, app_name: str = None, app_settings: str = None
        ) -> str:
            """Stage notification settings."""
            import json

            parameters = {k: v for k, v in {"enabled": enabled, "do_not_disturb": do_not_disturb, "app_name": app_name, "app_settings": app_settings}.items() if v is not None}

            receipt = changeset.add(
                description=(
                    f"Set notifications: {', '.join(f'{k}={v}' for k, v in parameters.items())}"
                ),
                change_type="audio",
                script="set_notifications",
                parameters=parameters,
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://audio/notifications")
        def get_notifications_resource() -> str:
            """Return current notification settings."""
            import json

            return json.dumps(feature.get(), indent=2)


feature = NotificationsFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
