#!/usr/bin/env python3
"""
KDE Configuration Orchestrator
-------------------------------
Centralised helper for writing KDE Plasma config entries via kwriteconfig6,
running kscreen-doctor commands, and reconfiguring KWin.

Every individual script delegates here so that:
  • There is exactly ONE place that shells out to kwriteconfig6.
  • Error-handling / logging is consistent everywhere.
  • Debugging is trivial: if a script fails you know the values are wrong;
    if the orchestrator fails you know the subprocess plumbing is wrong.
"""
import subprocess


# ── kwriteconfig6 helpers ────────────────────────────────────────────────


def write_kde_config(file: str, group: str, key: str, value: str) -> bool:
    """Write a single KDE config entry via kwriteconfig6.

    Args:
        file:  Config filename (e.g. "kwinrc", "kdeglobals", "kcminputrc").
        group: INI group inside that file (e.g. "KDE", "Mouse").
        key:   Key name.
        value: Value to write (always a string).

    Returns:
        True on success, False on failure.
    """
    try:
        subprocess.run(
            [
                "kwriteconfig6",
                "--file",
                file,
                "--group",
                group,
                "--key",
                key,
                value,
            ],
            check=True,
            capture_output=True,
        )
        print(f"  ✓ [{file}] {group}/{key} = {value}")
        return True
    except FileNotFoundError:
        print(f"  ❌ kwriteconfig6 not found – cannot set {key}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error setting {key}: {e}")
        return False


def write_kde_configs(configs: list[tuple[str, str, str, str]]) -> bool:
    """Write multiple KDE config entries.

    Args:
        configs: List of (file, group, key, value) tuples.

    Returns:
        True if **all** writes succeeded.
    """
    all_success = True
    for file, group, key, value in configs:
        if not write_kde_config(file, group, key, value):
            all_success = False
    return all_success


# ── kscreen-doctor helper ────────────────────────────────────────────────


def run_kscreen_doctor(output_spec: str) -> bool:
    """Run kscreen-doctor with the given output spec.

    Args:
        output_spec: e.g. "output.1.scale.1.25"

    Returns:
        True on success, False on failure.
    """
    try:
        subprocess.run(
            ["kscreen-doctor", output_spec],
            check=True,
            capture_output=True,
        )
        print(f"  ✓ kscreen-doctor {output_spec}")
        return True
    except FileNotFoundError:
        print("  ❌ kscreen-doctor not found – skipping.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  kscreen-doctor error: {e}")
        return False


# ── KWin reconfigure helper ─────────────────────────────────────────────


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
        print("  🔄 KWin reconfigured")
        return True
    except FileNotFoundError:
        print("  ⚠️  qdbus not found – KWin reload skipped.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error reconfiguring KWin: {e}")
        return False
