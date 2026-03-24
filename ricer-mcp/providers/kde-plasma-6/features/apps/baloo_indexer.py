"""Feature: baloo file indexer (apps)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_config

from feature import FeatureType

class BalooIndexerFeature(Feature):
    type = FeatureType.APPS
    """Baloo indexer feature implementation."""

    def set(self, indexing_enabled: bool) -> bool:
        """Enable or disable Baloo file indexing globally."""
        # Note: actually controlling balooctl might be needed to stop the daemon instantly,
        # but kwriteconfig sets the persistence.
        import subprocess
        success = write_kde_config("baloofilerc", "Basic Settings", "Indexing-Enabled", str(indexing_enabled).lower())

        # Give a best-effort run to suspend/disable via balooctl
        if not indexing_enabled:
            try:
                subprocess.run(["balooctl", "suspend"], capture_output=True)
                subprocess.run(["balooctl", "disable"], capture_output=True)
            except FileNotFoundError:
                pass
        
        return success

    def get(self) -> dict:
        """Return current Baloo indexer settings."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "baloo_indexer",
            "values": {
                "indexing_enabled": read_kde_config("baloofilerc", "Basic Settings", "Indexing-Enabled", "true") == "true",
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_baloo_indexing(indexing_enabled: bool) -> str:
            """Stage Baloo file search indexing preference."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set Baloo indexing enabled: {indexing_enabled}"
                ),
                change_type="apps",
                script="set_baloo_indexing",
                parameters={
                    "indexing_enabled": indexing_enabled,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://apps/baloo-indexer")
        def get_baloo_indexer_resource() -> str:
            """Return current Baloo indexer settings."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = BalooIndexerFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
