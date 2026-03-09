"""Stage keyboard accessibility settings (input — requires session restart)."""


def register(mcp, changeset):
    @mcp.tool()
    def set_keyboard_accessibility(
        sticky_keys: bool,
        sticky_keys_latch: bool,
        slow_keys: bool,
        slow_keys_delay: int,
        bounce_keys: bool,
        bounce_keys_delay: int,
        repeat_rate: int,
        repeat_delay: int,
    ) -> str:
        """Stage keyboard accessibility feature changes.

        This does NOT apply the change immediately. It adds the change to the
        staging area. The change will only be executed when the user confirms
        it via confirm_change().

        Corresponds to script: set_keyboard_accessibility
        Change type: input (requires session restart to take full effect)

        Args:
            sticky_keys: Enable sticky keys (modifier keys stay active after
                         a single press).
            sticky_keys_latch: Enable sticky keys latch (pressing a modifier
                               twice locks it until pressed again).
            slow_keys: Enable slow keys (keys must be held for a minimum
                       duration before registering).
            slow_keys_delay: Slow keys delay in milliseconds (e.g. 300).
            bounce_keys: Enable bounce keys (ignore rapid repeated key presses).
            bounce_keys_delay: Bounce keys delay in milliseconds (e.g. 500).
            repeat_rate: Key repeat rate — keys per second when held (e.g. 25, 50).
            repeat_delay: Key repeat delay — milliseconds before repeat starts
                          (e.g. 300, 500, 660).

        Returns:
            JSON staging receipt with order number, script, and parameters.
        """
        import json

        # Build a human-readable description of what's being enabled
        features = []
        if sticky_keys:
            features.append("sticky keys")
        if slow_keys:
            features.append(f"slow keys ({slow_keys_delay}ms)")
        if bounce_keys:
            features.append(f"bounce keys ({bounce_keys_delay}ms)")
        features.append(f"repeat rate={repeat_rate}, delay={repeat_delay}ms")
        desc = "Set keyboard accessibility: " + ", ".join(features)

        receipt = changeset.add(
            description=desc,
            change_type="input",
            script="set_keyboard_accessibility",
            parameters={
                "sticky_keys": sticky_keys,
                "sticky_keys_latch": sticky_keys_latch,
                "slow_keys": slow_keys,
                "slow_keys_delay": slow_keys_delay,
                "bounce_keys": bounce_keys,
                "bounce_keys_delay": bounce_keys_delay,
                "repeat_rate": repeat_rate,
                "repeat_delay": repeat_delay,
            },
        )
        return json.dumps(receipt, indent=2)
