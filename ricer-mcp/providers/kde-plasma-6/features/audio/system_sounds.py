"""Feature: system sounds (audio)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs


from feature import FeatureType

class SystemSoundsFeature(Feature):
    type = FeatureType.AUDIO
    """System sounds feature implementation."""

    def set(self, enabled: bool = None, theme: str = None) -> bool:
        """Enable or disable system sounds and set the sound theme."""
        configs = []
        if enabled is not None:
            configs.append(("plasmanotifyrc", "Event Sounds", "enabled", str(enabled).lower()))
        if theme is not None:
            configs.append(("plasmanotifyrc", "Event Sounds", "theme", theme))
        
        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current system sounds settings as a structured payload."""
        from utils.read.kreadconfig import read_kde_configs

        configs = [
            ("plasmanotifyrc", "Event Sounds", "enabled", "true"),
            ("plasmanotifyrc", "Event Sounds", "theme", "ocean"),
        ]
        values = read_kde_configs(configs)
        failed_keys = [k for k, v in values.items() if v is None]

        return {
            "setting": "system_sounds",
            "file": "plasmanotifyrc",
            "group": "Event Sounds",
            "values": {
                "enabled": values.get("enabled") == "true",
                "theme": values.get("theme"),
            },
            "error": (
                "Failed to read plasmanotifyrc system sounds keys via kreadconfig6: "
                + ", ".join(failed_keys)
                if failed_keys
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_system_sounds(
            enabled: bool = None, theme: str = None
        ) -> str:
            """Stage system sounds settings."""
            import json

            parameters = {k: v for k, v in {"enabled": enabled, "theme": theme}.items() if v is not None}

            receipt = changeset.add(
                description=(
                    f"Set system sounds: {', '.join(f'{k}={v}' for k, v in parameters.items())}"
                ),
                change_type="audio",
                script="set_system_sounds",
                parameters=parameters,
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://audio/system-sounds")
        def get_system_sounds_resource() -> str:
            """Return current system sounds settings."""
            import json

            return json.dumps(feature.get(), indent=2)


feature = SystemSoundsFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
