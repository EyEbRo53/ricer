"""Stage a global display scaling change (display — applies live)."""


def register(mcp, changeset):
    @mcp.tool()
    def set_global_scaling(scale_value: float) -> str:
        """Stage a global UI scaling change.

        This does NOT apply the change immediately. It adds the change to the
        staging area. The change will only be executed when the user confirms
        it via confirm_change().

        Corresponds to script: set_global_scaling
        Change type: display (applies live via kscreen-doctor)

        Args:
            scale_value: Scaling factor (e.g. 1.0, 1.25, 1.5, 2.0).

        Returns:
            JSON staging receipt with order number, script, and parameters.
        """
        import json

        receipt = changeset.add(
            description=f"Set global scaling to {scale_value}×",
            change_type="display",
            script="set_global_scaling",
            parameters={"scale_value": scale_value},
        )
        return json.dumps(receipt, indent=2)
