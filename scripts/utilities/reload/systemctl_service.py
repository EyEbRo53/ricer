#!/usr/bin/env python3
"""Reload systemd user services."""
import subprocess


def systemctl_reload(service: str) -> bool:
    """Reload a systemd user service.

    Args:
        service: Service name (e.g., "plasma-kwin_wayland", "plasma-plasmashell").

    Returns:
        True on success, False on failure.
    """
    try:
        subprocess.run(
            ["systemctl", "--user", "reload", service],
            check=True,
            capture_output=True,
        )
        print(f"  ✓ {service} reloaded")
        return True
    except FileNotFoundError:
        print("  ❌ systemctl not found – service reload skipped")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error reloading {service}: {e}")
        return False


def systemctl_restart(service: str) -> bool:
    """Restart a systemd user service.

    Args:
        service: Service name (e.g., "plasma-kwin_wayland", "plasma-plasmashell").

    Returns:
        True on success, False on failure.
    """
    try:
        subprocess.run(
            ["systemctl", "--user", "restart", service],
            check=True,
            capture_output=True,
        )
        print(f"  ✓ {service} restarted")
        return True
    except FileNotFoundError:
        print("  ❌ systemctl not found – service restart skipped")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error restarting {service}: {e}")
        return False
