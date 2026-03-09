"""Stage a panel position change (display — applies live via DBus)."""


def register(mcp, changeset):
    @mcp.tool()
    def move_panel(position: str) -> str:
        """Stage a panel (taskbar) position change.

        This does NOT apply the change immediately. It adds the change to the
        staging area. The change will only be executed when the user confirms
        it via confirm_change().

        Corresponds to script: move_panel
        Change type: display (applies live via DBus/qdbus)

        Args:
            position: Panel location. One of "top", "bottom", "left", "right".

        Returns:
            JSON staging receipt with order number, script, and parameters.
        """
        import json

        receipt = changeset.add(
            description=f"Move panel to {position}",
            change_type="display",
            script="move_panel",
            parameters={"position": position},
        )
        return json.dumps(receipt, indent=2)
