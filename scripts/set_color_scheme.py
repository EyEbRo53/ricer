#!/usr/bin/env python3
"""Set KDE Plasma color scheme (theme) and apply immediately."""
from utilities.write.kwriteconfig import write_kde_config
from utilities.reload.reload_plasma_shell import reload_plasma_shell


def set_color_scheme(scheme: str) -> bool:
    """Configure color scheme via kwriteconfig6 and apply immediately.

    Args:
        scheme: Color scheme name (e.g. "Breeze", "BreezeDark", 
               "BreezeHighContrast", "BreezeHighContrastInverse", "Dracula").

    Returns:
        True on success, False on failure.
    """
    success = write_kde_config("kdeglobals", "General", "ColorScheme", scheme)
    if success:
        reload_plasma_shell()
    return success
