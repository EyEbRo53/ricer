#!/usr/bin/env python3
"""Restart Plasma shell."""
import subprocess
import shutil


def _get_start_command() -> list[str] | None:
    """Choose the best available command to start plasmashell."""
    if shutil.which("kstart6"):
        return ["kstart6", "plasmashell"]
    if shutil.which("kstart"):
        return ["kstart", "plasmashell"]
    if shutil.which("plasmashell"):
        # Direct fallback when kstart/kstart6 is unavailable.
        return ["plasmashell", "--replace"]
    return None


def reload_plasma_shell() -> bool:
    """Restart the Plasma shell for immediate changes.

    Returns:
        True on success, False on failure.
    """
    try:
        if shutil.which("plasmashell"):
            # Preferred path: ask plasmashell to replace the running shell.
            subprocess.Popen(
                ["plasmashell", "--replace"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("  ✓ Plasma shell restarted via plasmashell --replace")
            return True

        start_cmd = _get_start_command()
        if not start_cmd:
            print("  ❌ No command found to start plasmashell – reload skipped")
            return False

        if shutil.which("kquitapp6"):
            subprocess.run(
                ["kquitapp6", "plasmashell"],
                check=True,
                capture_output=True,
            )

        subprocess.run(start_cmd, check=True, capture_output=True)
        print("  ✓ Plasma shell restarted")
        return True
    except FileNotFoundError:
        print("  ❌ Plasma shell reload command missing – trying direct fallback")
        if shutil.which("plasmashell"):
            try:
                subprocess.Popen(
                    ["plasmashell", "--replace"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                print("  ✓ Plasma shell started via fallback")
                return True
            except subprocess.SubprocessError:
                pass
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error restarting Plasma shell: {e}")
        if shutil.which("plasmashell"):
            try:
                subprocess.Popen(
                    ["plasmashell", "--replace"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                print("  ✓ Plasma shell started via fallback")
                return True
            except subprocess.SubprocessError:
                pass
        return False
