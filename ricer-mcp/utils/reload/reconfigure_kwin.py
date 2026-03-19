#!/usr/bin/env python3
"""Reconfigure KWin via qdbus."""
import subprocess


def reconfigure_kwin() -> bool:
    """Ask KWin to reload its configuration via qdbus.

    Returns:
        True on success, False on failure.
    """
    try:
        subprocess.run(
            ["qdbus", "org.kde.KWin", "/KWin", "reconfigure"],
            check=True,
            capture_output=True,
        )
        print("  ✓ KWin reconfigured")
        return True
    except FileNotFoundError:
        print("  ❌ qdbus not found – KWin reconfigure skipped")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error reconfiguring KWin: {e}")
        return False
