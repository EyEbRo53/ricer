"""Feature: keyboard accessibility (input)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs
from utils.reload.reconfigure_kwin import reconfigure_kwin


from feature import FeatureType

class KeyboardAccessibilityFeature(Feature):
    type = FeatureType.INPUT
    """Keyboard accessibility feature implementation."""

    def set(
        self,
        sticky_keys: bool,
        sticky_keys_latch: bool,
        slow_keys: bool,
        slow_keys_delay: int,
        bounce_keys: bool,
        bounce_keys_delay: int,
        repeat_rate: int,
        repeat_delay: int,
    ) -> bool:
        """Configure sticky keys, slow keys, bounce keys, and repeat settings."""
        configs = [
            ("kaccessrc", "Keyboard", "StickyKeys", "true" if sticky_keys else "false"),
            (
                "kaccessrc",
                "Keyboard",
                "StickyKeysLatch",
                "true" if sticky_keys_latch else "false",
            ),
            ("kaccessrc", "Keyboard", "SlowKeys", "true" if slow_keys else "false"),
            ("kaccessrc", "Keyboard", "SlowKeysDelay", str(slow_keys_delay)),
            ("kaccessrc", "Keyboard", "BounceKeys", "true" if bounce_keys else "false"),
            ("kaccessrc", "Keyboard", "BounceKeysDelay", str(bounce_keys_delay)),
            ("kaccessrc", "Keyboard", "RepeatRate", str(repeat_rate)),
            ("kaccessrc", "Keyboard", "RepeatDelay", str(repeat_delay)),
        ]

        success = write_kde_configs(configs)
        reconfigure_kwin()
        return success

    def get(self) -> dict:
        """Return current keyboard accessibility states as structured payload."""
        from utils.kde_config_reader import read_kde_configs

        configs = [
            ("kaccessrc", "Keyboard", "StickyKeys", "false"),
            ("kaccessrc", "Keyboard", "StickyKeysLatch", "false"),
            ("kaccessrc", "Keyboard", "SlowKeys", "false"),
            ("kaccessrc", "Keyboard", "SlowKeysDelay", "0"),
            ("kaccessrc", "Keyboard", "BounceKeys", "false"),
            ("kaccessrc", "Keyboard", "BounceKeysDelay", "0"),
            ("kaccessrc", "Keyboard", "RepeatRate", "25"),
            ("kaccessrc", "Keyboard", "RepeatDelay", "660"),
        ]
        values = read_kde_configs(configs)
        failed_keys = [k for k, v in values.items() if v is None]

        def _bool(v):
            return v.lower() == "true" if v else False

        def _int_or_raw(v):
            try:
                return int(v) if v else v
            except (ValueError, TypeError):
                return v

        return {
            "setting": "keyboard_accessibility",
            "file": "kaccessrc",
            "group": "Keyboard",
            "values": {
                "sticky_keys": _bool(values.get("StickyKeys")),
                "sticky_keys_latch": _bool(values.get("StickyKeysLatch")),
                "slow_keys": _bool(values.get("SlowKeys")),
                "slow_keys_delay": _int_or_raw(values.get("SlowKeysDelay")),
                "bounce_keys": _bool(values.get("BounceKeys")),
                "bounce_keys_delay": _int_or_raw(values.get("BounceKeysDelay")),
                "repeat_rate": _int_or_raw(values.get("RepeatRate")),
                "repeat_delay": _int_or_raw(values.get("RepeatDelay")),
            },
            "error": (
                "Failed to read kaccessrc keys via kreadconfig6: "
                + ", ".join(failed_keys)
                if failed_keys
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
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
            """Stage keyboard accessibility feature changes."""
            import json

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

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://input/keyboard-accessibility")
        def get_keyboard_accessibility_resource() -> str:
            """Return current keyboard accessibility feature states."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = KeyboardAccessibilityFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
