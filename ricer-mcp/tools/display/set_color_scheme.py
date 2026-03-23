"""Stage a color scheme change (display — applies immediately via kwriteconfig6)."""


def register(mcp, changeset):
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
