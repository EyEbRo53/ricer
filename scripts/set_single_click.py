#!/usr/bin/env python3
"""Enable single-click to open for reduced motor precision needs."""
from utilities.kde_config_orchestrator import write_kde_config


def set_single_click(enabled):
    """Configure single-click to open via orchestrator."""
    value = "true" if enabled else "false"
    return write_kde_config("kdeglobals", "KDE", "SingleClick", value)


if __name__ == "__main__":
    set_single_click(True)
