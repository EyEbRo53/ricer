#!/usr/bin/env python3
"""Set KDE Plasma wallpaper."""
import os
from utilities.write.plasma_script import run_plasma_script


def set_wallpaper(path: str) -> bool:
    """Set KDE Plasma wallpaper via orchestrator.

    Args:
        path: Full path to the wallpaper image file.

    Returns:
        True on success, False on failure.
    """
    script = f"""
    var allDesktops = desktops();
    for (i=0; i<allDesktops.length; i++) {{
        d = allDesktops[i];
        d.wallpaperPlugin = "org.kde.image";
        d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
        d.writeConfig("Image", "file://{path}");
    }}
    """
    return run_plasma_script(script, f"Wallpaper set: {os.path.basename(path)}")



