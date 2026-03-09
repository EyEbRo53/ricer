"""Stage a double-click interval change (input — requires session restart)."""


def register(mcp, changeset):
    @mcp.tool()
    def set_double_click_interval(interval: int) -> str:
        """Stage a double-click interval change.

        This does NOT apply the change immediately. It adds the change to the
        staging area. The change will only be executed when the user confirms
        it via confirm_change().

        Corresponds to script: set_double_click_interval
        Change type: input (requires session restart to take full effect)

        Args:
            interval: Double-click interval in milliseconds (e.g. 400, 600, 800).
                      Higher values give more time between clicks.

        Returns:
            JSON staging receipt with order number, script, and parameters.
        """
        import json

        receipt = changeset.add(
            description=f"Set double-click interval to {interval}ms",
            change_type="input",
            script="set_double_click_interval",
            parameters={"interval": interval},
        )
        return json.dumps(receipt, indent=2)
