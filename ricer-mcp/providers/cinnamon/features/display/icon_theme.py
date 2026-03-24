"""Feature: icon theme (display)."""

from feature import Feature, FeatureType


class IconThemeFeature(Feature):
    """Icon theme feature implementation for Cinnamon."""
    type = FeatureType.DISPLAY

    def set(self, theme: str) -> bool:
        """Set Cinnamon icon theme via gsettings."""
        from utils.write.gsettings_writer import write_gsetting

        return write_gsetting(
            "org.cinnamon.desktop.interface", "icon-theme", f"'{theme}'"
        )

    def get(self) -> dict:
        """Return current icon theme as structured payload."""
        from utils.read.gsettings_reader import read_gsetting

        value = read_gsetting("org.cinnamon.desktop.interface", "icon-theme", "Mint-Y")
        return {
            "setting": "icon_theme",
            "schema": "org.cinnamon.desktop.interface",
            "key": "icon-theme",
            "value": value,
            "description": "Current icon theme used by Cinnamon",
            "error": (
                "Failed to read icon-theme from gsettings."
                if value is None
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_icon_theme(theme: str) -> str:
            """Stage an icon theme change.

            Args:
                theme: Icon theme name. Examples: "Mint-Y", "Mint-Y-Purple",
                       "Papirus", "Papirus-Dark", "Numix-Circle", etc.

            Returns:
                JSON staging receipt with order number, script, and parameters.
            """
            import json

            receipt = changeset.add(
                description=f"Set icon theme to {theme}",
                change_type="display",
                script="set_icon_theme",
                parameters={"theme": theme},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("cinnamon://display/icon-theme")
        def get_icon_theme_resource() -> str:
            """Return the current icon theme name."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = IconThemeFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
