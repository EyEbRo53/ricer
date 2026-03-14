#!/usr/bin/env python3
# scripts/set_cursor_size.py
"""Set cursor size for improved visibility and apply immediately."""
from utilities.write.kwriteconfig import write_kde_config
from utilities.reload.reconfigure_kwin import reconfigure_kwin


def set_cursor_size(size):
    """Configure cursor size via orchestrator and apply immediately."""
    success = write_kde_config("kcminputrc", "Mouse", "cursorSize", str(size))
    if success:
        reconfigure_kwin()
    return success


