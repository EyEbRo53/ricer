#!/usr/bin/env python3
"""Read Plasma shell state via qdbus."""
import subprocess


def read_current_wallpaper() -> str | None:
    """Read the current wallpaper path via DBus (Plasma shell).

    Returns:
        The image path string, or None on failure.
    """
    script = """
    var allDesktops = desktops();
    if (allDesktops.length > 0) {
        var d = allDesktops[0];
        d.wallpaperPlugin = "org.kde.image";
        d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
        print(d.readConfig("Image"));
    }
    """
    try:
        result = subprocess.run(
            [
                "qdbus",
                "org.kde.plasmashell",
                "/PlasmaShell",
                "org.kde.PlasmaShell.evaluateScript",
                script,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        path = result.stdout.strip()
        # Strip file:// prefix if present
        if path.startswith("file://"):
            path = path[7:]
        return path or None
    except FileNotFoundError:
        print("  ❌ qdbus not found – cannot read wallpaper")
        return None
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Could not read wallpaper: {e}")
        return None


def read_panel_position() -> str | None:
    """Read the current panel position via DBus (Plasma shell).

    Returns:
        The panel location string (e.g. "top", "bottom", "left", "right"),
        or None on failure.
    """
    script = """
    var panels = panels();
    if (panels.length > 0) {
        print(panels[0].location);
    }
    """
    try:
        result = subprocess.run(
            [
                "qdbus",
                "org.kde.plasmashell",
                "/PlasmaShell",
                "org.kde.PlasmaShell.evaluateScript",
                script,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or None
    except FileNotFoundError:
        print("  ❌ qdbus not found – cannot read panel position")
        return None
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Could not read panel position: {e}")
        return None
