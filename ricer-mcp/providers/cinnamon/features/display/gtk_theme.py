"""Feature: GTK theme (display)."""

from feature import Feature, FeatureType


class GtkThemeFeature(Feature):
    """GTK theme feature implementation for Cinnamon."""
    type = FeatureType.DISPLAY

    def set(self, theme: str) -> bool:
        """Set Cinnamon GTK theme via gsettings."""
        from utils.write.gsettings_writer import write_gsetting

        return write_gsetting(
            "org.cinnamon.desktop.interface", "gtk-theme", f"'{theme}'"
        )

    def get(self) -> dict:
        """Return current GTK theme as structured payload."""
        from utils.read.gsettings_reader import read_gsetting

        value = read_gsetting("org.cinnamon.desktop.interface", "gtk-theme", "Mint-Y")
        return {
            "setting": "gtk_theme",
            "schema": "org.cinnamon.desktop.interface",
            "key": "gtk-theme",
            "value": value,
            "description": "Current GTK theme used by Cinnamon",
            "error": (
                "Failed to read gtk-theme from gsettings."
                if value is None
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_gtk_theme(theme: str) -> str:
            """Stage a GTK theme change.

            Args:
                theme: GTK theme name. Examples: "Mint-Y", "Mint-Y-Dark",
                       "Mint-Y-Dark-Purple", "Adwaita", "Arc-Dark", etc.

            Returns:
                JSON staging receipt with order number, script, and parameters.
            """
            import json

            receipt = changeset.add(
                description=f"Set GTK theme to {theme}",
                change_type="display",
                script="set_gtk_theme",
                parameters={"theme": theme},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("cinnamon://display/gtk-theme")
        def get_gtk_theme_resource() -> str:
            """Return the current GTK theme name."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = GtkThemeFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
