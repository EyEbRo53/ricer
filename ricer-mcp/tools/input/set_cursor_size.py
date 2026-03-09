"""Stage a cursor size change (input — requires session restart)."""


def register(mcp, changeset):
    @mcp.tool()
    def set_cursor_size(size: int) -> str:
        """Stage a cursor size change.

        This does NOT apply the change immediately. It adds the change to the
        staging area. The change will only be executed when the user confirms
        it via confirm_change().

        Corresponds to script: set_cursor_size
        Change type: input (requires session restart to take full effect)

        Args:
            size: Cursor size in pixels (e.g. 24, 36, 48, 64).

        Returns:
            JSON staging receipt with order number, script, and parameters.
        """
        import json

        receipt = changeset.add(
            description=f"Set cursor size to {size}px",
            change_type="input",
            script="set_cursor_size",
            parameters={"size": size},
        )
        return json.dumps(receipt, indent=2)
