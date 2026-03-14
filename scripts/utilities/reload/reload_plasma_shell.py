#!/usr/bin/env python3
"""Restart Plasma shell."""
import subprocess


def reload_plasma_shell() -> bool:
    """Restart the Plasma shell for immediate changes.

    Returns:
        True on success, False on failure.
    """
    try:
        subprocess.run(["kquitapp6", "plasmashell"], check=True, capture_output=True)
        subprocess.run(["kstart", "plasmashell"], check=True, capture_output=True)
        print("  ✓ Plasma shell restarted")
        return True
    except FileNotFoundError:
        print("  ❌ kquitapp6 or kstart not found – Plasma shell reload skipped")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error restarting Plasma shell: {e}")
        return False
