#!/usr/bin/env python3
"""Read KDE config entries via kreadconfig6."""
import subprocess


def read_kde_config(file: str, group: str | list[str], key: str, default: str = "") -> str | None:
    """Read a single KDE config entry via kreadconfig6.

    Args:
        file:    Config filename (e.g. "kwinrc", "kdeglobals", "kcminputrc").
        group:   INI group inside that file (e.g. "KDE", "Mouse"). Can be a list of strings for nested groups.
        key:     Key name.
        default: Value returned by kreadconfig6 when the key is absent.

    Returns:
        The current value as a string, or *None* if the read failed entirely
        (e.g. kreadconfig6 not installed).
    """
    cmd = [
        "kreadconfig6",
        "--file", file,
    ]
    if isinstance(group, list):
        for g in group:
            cmd += ["--group", g]
    else:
        cmd += ["--group", group]
    cmd += ["--key", key]
    if default:
        cmd += ["--default", default]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        value = result.stdout.strip()
        return value
    except FileNotFoundError:
        print(f"  ❌ kreadconfig6 not found – cannot read {key}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error reading {key}: {e}")
        return None


def read_kde_configs(
    configs: list[tuple[str, str | list[str], str, str]],
) -> dict[str, str | None]:
    """Read multiple KDE config entries.

    Args:
        configs: List of (file, group(s), key, default) tuples.

    Returns:
        Dict mapping each key to its current value (or None on failure).
    """
    results: dict[str, str | None] = {}
    for file, group, key, default in configs:
        results[key] = read_kde_config(file, group, key, default)
    return results
