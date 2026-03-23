"""Feature: color_scheme (display)."""

from feature import Feature


from feature import FeatureType

class ColorSchemeFeature(Feature):
    type = FeatureType.DISPLAY
    """Color scheme (theme) feature implementation."""

    def set(self, scheme: str) -> bool:
        """Set KDE Plasma color scheme via kwriteconfig6 and apply immediately."""
        from utils.write.kwriteconfig import write_kde_config
        from utils.reload.reload_plasma_shell import reload_plasma_shell

        success = write_kde_config("kdeglobals", "General", "ColorScheme", scheme)
        if success:
            reload_plasma_shell()
        return success

    def get(self) -> dict:
        """Return current color scheme as a structured payload."""
        from utils.kde_config_reader import read_kde_config

        value = read_kde_config("kdeglobals", "General", "ColorScheme", "Breeze")
        return {
            "setting": "color_scheme",
            "file": "kdeglobals",
            "group": "General",
            "key": "ColorScheme",
            "value": value,
            "description": "Current color scheme/theme used by KDE Plasma",
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_color_scheme(scheme: str) -> str:
            """Stage a color scheme (theme) change.

            This does NOT apply the change immediately. It adds the change to the
            staging area. The change will only be executed when the user confirms
            it via confirm_change().

            Corresponds to script: set_color_scheme
            Change type: display (applies immediately via kwriteconfig6 + plasma reload)

            Args:
                scheme: Color scheme name. Examples: "Breeze", "BreezeDark",
                       "BreezeHighContrast", "BreezeHighContrastInverse", "Dracula", etc.
                       High-contrast themes are recommended for colorblind accessibility.

            Returns:
                JSON staging receipt with order number, script, and parameters.
            """
            import json

            receipt = changeset.add(
                description=f"Set color scheme to {scheme}",
                change_type="display",
                script="set_color_scheme",
                parameters={"scheme": scheme},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://display/color-scheme")
        def get_color_scheme_resource() -> str:
            """Return the current active color scheme.

            Reads [General] ColorScheme from kdeglobals via kreadconfig6.

            Corresponds to tool: set_color_scheme
            """
            import json
            return json.dumps(feature.get(), indent=2)


feature = ColorSchemeFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
