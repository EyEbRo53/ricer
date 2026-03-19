#!/usr/bin/env python3
"""Restart kded6 daemon."""
import subprocess


def restart_kded() -> bool:
    """Restart kded6 daemon to apply keyboard accessibility immediately.

    Uses killall to stop the current daemon and starts a new instance directly.
    Falls back to systemd user service restart if direct method fails.

    Returns:
        True on success, False on failure.
    """
    # Try direct restart first
    try:
        subprocess.run(["killall", "kded6"], check=True, capture_output=True)
        subprocess.Popen(["/usr/bin/kded6"])
        print("  ✓ kded6 restarted")
        return True
    except FileNotFoundError:
        pass  # Try systemd fallback
    except subprocess.CalledProcessError:
        pass  # Try systemd fallback

    # Fallback to systemd user service restart
    for service in ("plasma-kded.service", "kded6.service", "kded.service"):
        try:
            subprocess.run(
                ["systemctl", "--user", "restart", service],
                check=True,
                capture_output=True,
            )
            print(f"  ✓ kded6 restarted via systemd ({service})")
            return True
        except FileNotFoundError:
            print("  ❌ systemctl not found – cannot restart kded6")
            return False
        except subprocess.CalledProcessError:
            continue

    print("  ⚠️  kded6 restart failed (no working method)")
    return False
