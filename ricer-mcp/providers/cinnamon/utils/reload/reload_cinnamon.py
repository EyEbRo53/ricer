#!/usr/bin/env python3
"""Reload / restart Cinnamon desktop components."""
import subprocess


def reload_cinnamon() -> bool:
    """Restart the Cinnamon shell (equivalent to Alt+F2 → 'r').

    Uses ``cinnamon --replace`` via nohup so the process survives
    the parent Python process exiting.

    Returns:
        True if the restart command was dispatched, False on error.
    """
    try:
        subprocess.Popen(
            ["nohup", "cinnamon", "--replace"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        print("  ✓ Cinnamon shell restart dispatched.")
        return True
    except FileNotFoundError:
        print("  ❌ 'cinnamon' binary not found – cannot restart shell.")
        return False
    except Exception as e:
        print(f"  ⚠️  Error restarting Cinnamon: {e}")
        return False


def restart_cinnamon_settings() -> bool:
    """Restart the cinnamon-settings-daemon.

    Useful after changes that the settings daemon needs to pick up
    (e.g. keyboard, power, xsettings).

    Returns:
        True if the restart commands were dispatched, False on error.
    """
    try:
        subprocess.run(
            ["pkill", "-f", "cinnamon-settings-daemon"],
            capture_output=True,
        )
        subprocess.Popen(
            ["cinnamon-settings-daemon"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        print("  ✓ cinnamon-settings-daemon restarted.")
        return True
    except FileNotFoundError:
        print("  ❌ cinnamon-settings-daemon not found.")
        return False
    except Exception as e:
        print(f"  ⚠️  Error restarting cinnamon-settings-daemon: {e}")
        return False
