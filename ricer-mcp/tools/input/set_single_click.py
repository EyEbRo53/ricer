"""Stage a single-click mode change (input — requires session restart)."""


def register(mcp, changeset):
    @mcp.tool()
    def set_single_click(enabled: bool) -> str:
        """Stage a single-click to open files/folders change.

        This does NOT apply the change immediately. It adds the change to the
        staging area. The change will only be executed when the user confirms
        it via confirm_change().

        Corresponds to script: set_single_click
        Change type: input (requires session restart to take full effect)

        Args:
            enabled: True to enable single-click to open, False for double-click.

        Returns:
            JSON staging receipt with order number, script, and parameters.
        """
        import json

        state = "enabled" if enabled else "disabled"
        receipt = changeset.add(
            description=f"Set single-click to open: {state}",
            change_type="input",
            script="set_single_click",
            parameters={"enabled": enabled},
        )
        return json.dumps(receipt, indent=2)
