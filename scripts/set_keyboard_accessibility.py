#!/usr/bin/env python3
# scripts/set_keyboard_accessibility.py
"""Configure keyboard accessibility features and apply immediately in KDE Plasma."""
from utilities.write.kwriteconfig import write_kde_configs
from utilities.reload.reconfigure_kwin import reconfigure_kwin


def set_keyboard_accessibility(
    sticky_keys,
    sticky_keys_latch,
    slow_keys,
    slow_keys_delay,
    bounce_keys,
    bounce_keys_delay,
    repeat_rate,
    repeat_delay,
):
    """Configure sticky keys, slow keys, bounce keys, and repeat settings.

    Args:
        sticky_keys (bool): Enable sticky keys
        sticky_keys_latch (bool): Enable sticky keys latch
        slow_keys (bool): Enable slow keys
        slow_keys_delay (int): Slow keys delay in ms
        bounce_keys (bool): Enable bounce keys
        bounce_keys_delay (int): Bounce keys delay in ms
        repeat_rate (int): Key repeat rate
        repeat_delay (int): Key repeat delay in ms

    Returns:
        bool: True if all settings applied successfully
    """
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


