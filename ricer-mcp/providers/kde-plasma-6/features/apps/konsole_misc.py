"""Feature: konsole miscellaneous settings (apps)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_config

from feature import FeatureType

class KonsoleMiscFeature(Feature):
    type = FeatureType.APPS
    """Konsole terminal feature implementation."""

    def set(self, tab_bar_visibility: int = None) -> bool:
        """Configure Konsole tab bar visibility.
        0=Always, 1=When Needed, 2=Never
        """
        if tab_bar_visibility is not None:
            return write_kde_config("konsolerc", "TabBar", "TabBarVisibility", str(tab_bar_visibility))
        return True

    def get(self) -> dict:
        """Return current konsole settings."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "konsole_misc",
            "values": {
                "tab_bar_visibility": read_kde_config("konsolerc", "TabBar", "TabBarVisibility", "1"),
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_konsole_misc(
            tab_bar_visibility: int = None
        ) -> str:
            """Stage Konsole miscellaneous settings (like tab bar visibility)."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set Konsole misc settings: tab_bar_visibility={tab_bar_visibility}"
                ),
                change_type="apps",
                script="set_konsole_misc",
                parameters={
                    "tab_bar_visibility": tab_bar_visibility,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://apps/konsole-misc")
        def get_konsole_misc_resource() -> str:
            """Return current Konsole misc settings."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = KonsoleMiscFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
