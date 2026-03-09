"""Resource: current keyboard accessibility settings (input — reads from kaccessrc)."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))


def register(mcp):
    @mcp.resource("plasma://input/keyboard-accessibility")
    def get_keyboard_accessibility() -> str:
        """Return current keyboard accessibility feature states.

        Reads [Keyboard] StickyKeys / StickyKeysLatch / SlowKeys /
        SlowKeysDelay / BounceKeys / BounceKeysDelay / RepeatRate /
        RepeatDelay from kaccessrc via kreadconfig6.

        Corresponds to tool: set_keyboard_accessibility
        """
        import json
        from utilities.kde_config_reader import read_kde_configs

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

        def _bool(v):
            return v.lower() == "true" if v else False

        def _int_or_raw(v):
            try:
                return int(v) if v else v
            except (ValueError, TypeError):
                return v

        return json.dumps(
            {
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
            },
            indent=2,
        )
