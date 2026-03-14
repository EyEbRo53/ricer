"""Backward-compatible read utility exports.

This module keeps legacy imports working:
    from utilities.kde_config_reader import ...

The implementation now lives under ``utilities.read``.
"""

from .read import (
    read_current_wallpaper,
    read_kde_config,
    read_kde_configs,
    read_kscreen_doctor,
    read_panel_position,
)

__all__ = [
    "read_kde_config",
    "read_kde_configs",
    "read_kscreen_doctor",
    "read_current_wallpaper",
    "read_panel_position",
]
