"""Stage touchpad sensitivity settings (input — requires session restart)."""


def register(mcp, changeset):
    @mcp.tool()
    def set_touchpad_settings(
        acceleration: float, speed: float, deceleration: float
    ) -> str:
        """Stage touchpad sensitivity and acceleration settings.

        This does NOT apply the change immediately. It adds the change to the
        staging area. The change will only be executed when the user confirms
        it via confirm_change().

        Corresponds to script: set_touchpad_settings
        Change type: input (requires session restart to take full effect)

        Args:
            acceleration: Acceleration multiplier (e.g. 0.5, 1.0, 1.5).
            speed: Pointer speed (e.g. 1, 3, 5).
            deceleration: Deceleration multiplier (e.g. 1.0, 1.5).

        Returns:
            JSON staging receipt with order number, script, and parameters.
        """
        import json

        receipt = changeset.add(
            description=(
                f"Set touchpad settings: acceleration={acceleration}, "
                f"speed={speed}, deceleration={deceleration}"
            ),
            change_type="input",
            script="set_touchpad_settings",
            parameters={
                "acceleration": acceleration,
                "speed": speed,
                "deceleration": deceleration,
            },
        )
        return json.dumps(receipt, indent=2)
