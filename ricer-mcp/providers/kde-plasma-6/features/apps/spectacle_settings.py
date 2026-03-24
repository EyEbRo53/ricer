"""Feature: spectacle settings (apps)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs

from feature import FeatureType

class SpectacleSettingsFeature(Feature):
    type = FeatureType.APPS
    """Spectacle settings feature implementation."""

    def set(self, save_location: str = None, filename_format: str = None) -> bool:
        """Configure Spectacle screenshot tool save path and filename format."""
        configs = []
        if save_location is not None:
            configs.append(("spectaclerc", "General", "SaveLocation", save_location))
        if filename_format is not None:
            configs.append(("spectaclerc", "General", "FilenameFormat", filename_format))

        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current Spectacle settings."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "spectacle_settings",
            "values": {
                "save_location": read_kde_config("spectaclerc", "General", "SaveLocation", ""),
                "filename_format": read_kde_config("spectaclerc", "General", "FilenameFormat", ""),
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_spectacle_settings(
            save_location: str = None, filename_format: str = None
        ) -> str:
            """Stage Spectacle screenshot settings."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set Spectacle settings: save_location={save_location}, format={filename_format}"
                ),
                change_type="apps",
                script="set_spectacle_settings",
                parameters={
                    "save_location": save_location,
                    "filename_format": filename_format,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://apps/spectacle-settings")
        def get_spectacle_settings_resource() -> str:
            """Return current Spectacle screenshot settings."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = SpectacleSettingsFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
