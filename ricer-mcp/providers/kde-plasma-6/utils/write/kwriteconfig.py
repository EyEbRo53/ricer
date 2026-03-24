#!/usr/bin/env python3
"""KDE config writer via kwriteconfig6."""
import subprocess


def write_kde_config(file: str, group: str | list[str], key: str, value: str) -> bool:
    """Write a single KDE config entry via kwriteconfig6.

    Args:
        file:  Config filename (e.g. "kwinrc", "kdeglobals", "kcminputrc").
        group: INI group inside that file. Can be a list for nested groups.
        key:   Key name.
        value: Value to write (always a string).

    Returns:
        True on success, False on failure.
    """
    try:
        cmd = [
            "kwriteconfig6",
            "--file",
            file,
        ]
        if isinstance(group, list):
            for g in group:
                cmd += ["--group", g]
        else:
            cmd += ["--group", group]
        cmd += ["--key", key, value]
        subprocess.run(
            cmd,
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


def write_kde_configs(configs: list[tuple[str, str | list[str], str, str]]) -> bool:
    """Write multiple KDE config entries.

    Args:
        configs: List of (file, group(s), key, value) tuples.

    Returns:
        True if **all** writes succeeded.
    """
    all_success = True
    for file, group, key, value in configs:
        if not write_kde_config(file, group, key, value):
            all_success = False
    return all_success
