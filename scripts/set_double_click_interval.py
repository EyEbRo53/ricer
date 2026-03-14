#!/usr/bin/env python3
"""Set double-click interval for users with slower clicking."""
from utilities.write.kwriteconfig import write_kde_config


def set_double_click_interval(interval):
    """Configure double-click interval via orchestrator."""
    return write_kde_config("kdeglobals", "KDE", "DoubleClickInterval", str(interval))


