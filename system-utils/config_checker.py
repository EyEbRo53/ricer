"""
Config Checker
--------------
Verifies that a script execution actually changed KDE config to the
expected values.  Stateless — each call is independent.

Uses kde_config_reader (via kreadconfig6) to read back config files.
Scripts that operate through DBus or kscreen-doctor are not verifiable
via config files and return True optimistically.
"""

from __future__ import annotations

import sys
import os

# Allow importing the kde_config_reader utility from /ricer-mcp/utils/
_RICER_MCP_DIR = os.path.join(os.path.dirname(__file__), "..", "ricer-mcp")
if _RICER_MCP_DIR not in sys.path:
    sys.path.insert(0, _RICER_MCP_DIR)

from utils.kde_config_reader import read_kde_config


# ── Verification map ────────────────────────────────────────────────
#
# Maps script_name → list of tuples:
#   (config_file, group, key, param_key, to_config_str, from_config_str)
#
# • param_key      : which key in parameters dict holds the expected value
# • to_config_str  : callable that converts the param value to the string
#                    that kreadconfig6 is expected to return
# • from_config_str: callable that converts a config string back to the
#                    Python type the script expects (used by undo)
#
# Scripts set to None use DBus / kscreen-doctor and cannot be verified
# through config files — verify() returns True for them.

_BOOL_TO_CFG = lambda v: "true" if v else "false"
_CFG_TO_BOOL = lambda s: s.lower() == "true"

_CONFIG_MAP: dict[str, list[tuple] | None] = {
    "set_cursor_size": [
        ("kcminputrc", "Mouse", "cursorSize", "size", str, int),
    ],
    "set_double_click_interval": [
        ("kdeglobals", "KDE", "DoubleClickInterval", "interval", str, int),
    ],
    "set_single_click": [
        ("kdeglobals", "KDE", "SingleClick", "enabled",
         _BOOL_TO_CFG, _CFG_TO_BOOL),
    ],
    "set_touchpad_settings": [
        ("kcminputrc", "Touchpad", "Acceleration", "acceleration", str, float),
        ("kcminputrc", "Touchpad", "Speed", "speed", str, float),
        ("kcminputrc", "Touchpad", "Deceleration", "deceleration", str, float),
    ],
    "set_keyboard_accessibility": [
        ("kaccessrc", "Keyboard", "StickyKeys", "sticky_keys",
         _BOOL_TO_CFG, _CFG_TO_BOOL),
        ("kaccessrc", "Keyboard", "StickyKeysLatch", "sticky_keys_latch",
         _BOOL_TO_CFG, _CFG_TO_BOOL),
        ("kaccessrc", "Keyboard", "SlowKeys", "slow_keys",
         _BOOL_TO_CFG, _CFG_TO_BOOL),
        ("kaccessrc", "Keyboard", "SlowKeysDelay", "slow_keys_delay", str, int),
        ("kaccessrc", "Keyboard", "BounceKeys", "bounce_keys",
         _BOOL_TO_CFG, _CFG_TO_BOOL),
        ("kaccessrc", "Keyboard", "BounceKeysDelay", "bounce_keys_delay", str, int),
        ("kaccessrc", "Keyboard", "RepeatRate", "repeat_rate", str, int),
        ("kaccessrc", "Keyboard", "RepeatDelay", "repeat_delay", str, int),
    ],
    "set_window_borders": [
        ("kwinrc", "org.kde.kdecoration2", "BorderSize", "border_size", str, str),
        ("kwinrc", "Windows", "BorderSnapZone", "snap_zone", str, int),
    ],
    # DBus / kscreen-doctor — not verifiable through config files
    "set_global_scaling": None,
    "set_wallpaper": None,
    "move_panel": None,
}


class ConfigChecker:
    """Reads back KDE config values and compares them to expected values."""

    def read_current(self, script: str, parameters: dict) -> dict[str, str | None]:
        """Read the current config values for every key a script touches.

        Returns:
            Dict mapping ``"file/group/key"`` → current value string
            (empty dict for unverifiable scripts).
        """
        entries = _CONFIG_MAP.get(script)
        if entries is None:
            return {}

        result: dict[str, str | None] = {}
        for cfg_file, group, key, _param_key, _to_conv, _from_conv in entries:
            result[f"{cfg_file}/{group}/{key}"] = read_kde_config(cfg_file, group, key)
        return result

    def verify(self, script: str, parameters: dict) -> bool:
        """Check whether the config file values match *parameters*.

        Returns True when all keys match **or** when the script cannot be
        verified via config files (DBus / kscreen-doctor changes).
        """
        entries = _CONFIG_MAP.get(script)
        if entries is None:
            return True  # optimistic — can't verify

        for cfg_file, group, key, param_key, converter, _from_conv in entries:
            if param_key not in parameters:
                continue
            current = read_kde_config(cfg_file, group, key)
            expected = converter(parameters[param_key])
            if str(current).strip() != str(expected).strip():
                return False
        return True

    def reverse_parameters(self, script: str, config_snapshot: dict) -> dict:
        """Convert a config snapshot back to script parameter format.

        Given a dict of ``"file/group/key" → config_string`` (as returned
        by :meth:`read_current`), rebuild the ``parameters`` dict that the
        script expects, using the *from_config_str* converter defined in
        ``_CONFIG_MAP``.

        Returns:
            Parameter dict suitable for passing to the script, or an empty
            dict for unverifiable scripts.
        """
        entries = _CONFIG_MAP.get(script)
        if entries is None:
            return {}

        params: dict = {}
        for cfg_file, group, key, param_key, _to_conv, from_conv in entries:
            config_key = f"{cfg_file}/{group}/{key}"
            value = config_snapshot.get(config_key)
            if value is None:
                continue
            try:
                params[param_key] = from_conv(value)
            except (ValueError, TypeError):
                params[param_key] = value
        return params
