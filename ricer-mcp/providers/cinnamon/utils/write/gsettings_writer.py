#!/usr/bin/env python3
"""Write Cinnamon/GTK config entries via gsettings."""
import subprocess


def write_gsetting(schema: str, key: str, value: str) -> bool:
    """Write a single gsettings value.

    Args:
        schema: GSettings schema (e.g. "org.cinnamon.desktop.interface").
        key:    Key name (e.g. "gtk-theme").
        value:  Value to write (always a string representation).

    Returns:
        True on success, False on failure.
    """
    cmd = ["gsettings", "set", schema, key, value]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"  ✓ [{schema}] {key} = {value}")
        return True
    except FileNotFoundError:
        print(f"  ❌ gsettings not found – cannot set {schema} {key}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error setting {schema} {key}: {e}")
        return False


def write_gsettings(configs: list[tuple[str, str, str]]) -> bool:
    """Write multiple gsettings values.

    Args:
        configs: List of (schema, key, value) tuples.

    Returns:
        True if **all** writes succeeded.
    """
    all_success = True
    for schema, key, value in configs:
        if not write_gsetting(schema, key, value):
            all_success = False
    return all_success
