#!/usr/bin/env python3
"""Reload KWin and kded to apply configuration changes immediately."""
import subprocess


def reload_kwin():
    """Reload KWin and Plasma shell for immediate changes."""
    success = True

    # Reload KWin
    try:
        subprocess.run(["qdbus", "org.kde.KWin", "/KWin", "reconfigure"], check=True)
        print("✓ KWin reconfigured")
    except Exception as e:
        print(f"⚠️ Failed to reconfigure KWin: {e}")
        success = False

    # Reload Plasma shell (Plasma 6 uses 'plasma' instead of 'plasmashell')
    try:
        subprocess.run(["kquitapp6", "plasma"], check=True)
        subprocess.run(["kstart", "plasma"], check=True)
        print("✓ Plasma shell restarted")
    except FileNotFoundError:
        print("⚠️ kquitapp6 or kstart not found, Plasma shell reload skipped")
        success = False
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to restart Plasma shell: {e}")
        success = False

    return success


def restart_kded():
    """Restart kded6 daemon to apply keyboard accessibility immediately.

    Uses killall to stop the current daemon and starts a new instance directly.
    """
    try:
        subprocess.run(["killall", "kded6"], check=True)
        subprocess.Popen(["/usr/bin/kded6"])
        print("✓ kded6 restarted, keyboard accessibility applied")
        return True
    except FileNotFoundError:
        print("⚠️ killall or /usr/bin/kded6 not found, kded6 restart skipped")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Failed to stop kded6: {e}")

    # Fallback to systemd user service restart
    for service in (
        "plasma-kded.service",
        "kded6.service",
        "kded.service",
    ):
        try:
            subprocess.run(
                ["systemctl", "--user", "restart", service],
                check=True,
            )
            print("✓ kded6 restarted via systemd, keyboard accessibility applied")
            return True
        except FileNotFoundError:
            print("⚠️ systemctl not found, cannot restart kded6")
            return False
        except subprocess.CalledProcessError:
            continue

    print("⚠️ kded6 restart failed (no working method)")
    return False


if __name__ == "__main__":
    reload_kwin()
    restart_kded()
