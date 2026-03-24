#!/usr/bin/env python3
"""Read Cinnamon/GTK config entries via gsettings."""
import subprocess


def read_gsetting(schema: str, key: str, default: str = "") -> str | None:
    """Read a single gsettings value.

    Args:
        schema: GSettings schema (e.g. "org.cinnamon.desktop.interface").
        key:    Key name (e.g. "gtk-theme").
        default: Returned when the read fails entirely.

    Returns:
        The current value as a string (with surrounding quotes stripped),
        or *None* if the read failed (e.g. gsettings not installed).
    """
    cmd = ["gsettings", "get", schema, key]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        value = result.stdout.strip()
        # gsettings wraps strings in single quotes: 'Mint-Y-Dark'
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        return value if value else default
    except FileNotFoundError:
        print(f"  ❌ gsettings not found – cannot read {schema} {key}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error reading {schema} {key}: {e}")
        return None


def read_gsettings(
    configs: list[tuple[str, str, str]],
) -> dict[str, str | None]:
    """Read multiple gsettings values.

    Args:
        configs: List of (schema, key, default) tuples.

    Returns:
        Dict mapping each key to its current value (or None on failure).
    """
    results: dict[str, str | None] = {}
    for schema, key, default in configs:
        results[key] = read_gsetting(schema, key, default)
    return results
