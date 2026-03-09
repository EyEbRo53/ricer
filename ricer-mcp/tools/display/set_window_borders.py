"""Stage a window borders change (display — applies after KWin reload)."""


def register(mcp, changeset):
    @mcp.tool()
    def set_window_borders(border_size: str, snap_zone: int) -> str:
        """Stage a window border size and snap zone change.

        This does NOT apply the change immediately. It adds the change to the
        staging area. The change will only be executed when the user confirms
        it via confirm_change().

        Corresponds to script: set_window_borders
        Change type: display (applies after KWin reconfigure)

        Args:
            border_size: Border size preset. One of "Tiny", "Normal", "Large",
                         "VeryLarge", "NoSides".
            snap_zone: Window snap zone in pixels (e.g. 10, 16).

        Returns:
            JSON staging receipt with order number, script, and parameters.
        """
        import json

        receipt = changeset.add(
            description=f"Set window borders to {border_size} with snap zone {snap_zone}px",
            change_type="display",
            script="set_window_borders",
            parameters={"border_size": border_size, "snap_zone": snap_zone},
        )
        return json.dumps(receipt, indent=2)
