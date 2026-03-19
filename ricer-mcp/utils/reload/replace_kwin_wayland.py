#!/usr/bin/env python3
"""Replace KWin Wayland compositor."""
import subprocess


def replace_kwin_wayland() -> bool:
    """Replace the KWin Wayland compositor.

    Runs kwin_wayland --replace in the background to restart the compositor
    without losing the session.

    Returns:
        True on success, False on failure.
    """
    try:
        subprocess.Popen(
            ["kwin_wayland", "--replace"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("  ✓ KWin Wayland compositor replaced")
        return True
    except FileNotFoundError:
        print("  ❌ kwin_wayland not found – compositor replace skipped")
        return False
    except subprocess.SubprocessError as e:
        print(f"  ⚠️  Error replacing compositor: {e}")
        return False
