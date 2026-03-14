#!/usr/bin/env python3
"""Configure window borders and snap zones for easier window manipulation."""
from utilities.write.kwriteconfig import write_kde_configs


def set_window_borders(border_size, snap_zone):
    """Configure titlebars, window borders and snap zones.

    Args:
        border_size: Border size (e.g., "Normal", "Large", "VeryLarge", "NoSides", "Tiny")
        snap_zone: Window snap zone in pixels (e.g., 10, 16)
    """
    configs = [
        ("kwinrc", "org.kde.kdecoration2", "BorderSize", str(border_size)),
        ("kwinrc", "Windows", "BorderSnapZone", str(snap_zone)),
    ]
    return write_kde_configs(configs)


