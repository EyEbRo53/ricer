#!/usr/bin/env python3
"""
KDE Configuration Reader
-------------------------
Centralised helper for *reading* KDE Plasma config entries via kreadconfig6
and querying kscreen-doctor output.

Mirror of kde_config_orchestrator.py (which writes), this module only reads.

Every MCP resource delegates here so that:
  • There is exactly ONE place that shells out to kreadconfig6.
  • Error-handling / logging is consistent everywhere.
  • The read side is fully decoupled from the write side.
"""
import subprocess
import json
import re


# ── kreadconfig6 helpers ─────────────────────────────────────────────────


def read_kde_config(file: str, group: str, key: str, default: str = "") -> str | None:
    """Read a single KDE config entry via kreadconfig6.

    Args:
        file:    Config filename (e.g. "kwinrc", "kdeglobals", "kcminputrc").
        group:   INI group inside that file (e.g. "KDE", "Mouse").
        key:     Key name.
        default: Value returned by kreadconfig6 when the key is absent.

    Returns:
        The current value as a string, or *None* if the read failed entirely
        (e.g. kreadconfig6 not installed).
    """
    cmd = [
        "kreadconfig6",
        "--file", file,
        "--group", group,
        "--key", key,
    ]
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
    configs: list[tuple[str, str, str, str]],
) -> dict[str, str | None]:
    """Read multiple KDE config entries.

    Args:
        configs: List of (file, group, key, default) tuples.

    Returns:
        Dict mapping each key to its current value (or None on failure).
    """
    results: dict[str, str | None] = {}
    for file, group, key, default in configs:
        results[key] = read_kde_config(file, group, key, default)
    return results


# ── kscreen-doctor query helper ──────────────────────────────────────────


def read_kscreen_doctor() -> dict | None:
    """Query kscreen-doctor for current output configuration.

    Parses ``kscreen-doctor --outputs`` (or ``-o``) and extracts the first
    output's scale and other useful properties.

    Returns:
        A dict with keys like ``name``, ``scale``, ``resolution``, ``enabled``
        for the first output, or None if the command fails.
    """
    try:
        result = subprocess.run(
            ["kscreen-doctor", "-o"],
            check=True,
            capture_output=True,
            text=True,
        )
        return _parse_kscreen_output(result.stdout)
    except FileNotFoundError:
        print("  ❌ kscreen-doctor not found – cannot read display info.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  kscreen-doctor error: {e}")
        return None


def _parse_kscreen_output(raw: str) -> dict:
    """Best-effort parser for kscreen-doctor -o output.

    Typical output looks like:
        Output: 1 eDP-1 enabled connected ...
            Modes: ...
            Scale: 1
            ...
    """
    info: dict = {}

    # Output name
    m = re.search(r"Output:\s+\d+\s+(\S+)", raw)
    if m:
        info["name"] = m.group(1)

    # Enabled / connected
    info["enabled"] = "enabled" in raw.lower()
    info["connected"] = "connected" in raw.lower()

    # Scale
    m = re.search(r"Scale:\s*([\d.]+)", raw, re.IGNORECASE)
    if m:
        info["scale"] = float(m.group(1))

    # Resolution (current mode, often marked with *)
    m = re.search(r"(\d{3,5}x\d{3,5}).*?\*", raw)
    if m:
        info["resolution"] = m.group(1)

    return info


# ── Wallpaper query helper ───────────────────────────────────────────────


def read_current_wallpaper() -> str | None:
    """Read the current wallpaper path via DBus (Plasma shell).

    Returns:
        The image path string, or None on failure.
    """
    script = """
    var allDesktops = desktops();
    if (allDesktops.length > 0) {
        var d = allDesktops[0];
        d.wallpaperPlugin = "org.kde.image";
        d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
        print(d.readConfig("Image"));
    }
    """
    try:
        result = subprocess.run(
            [
                "qdbus",
                "org.kde.plasmashell",
                "/PlasmaShell",
                "org.kde.PlasmaShell.evaluateScript",
                script,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        path = result.stdout.strip()
        # Strip file:// prefix if present
        if path.startswith("file://"):
            path = path[7:]
        return path or None
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"  ⚠️  Could not read wallpaper: {e}")
        return None


# ── Panel query helper ───────────────────────────────────────────────────


def read_panel_position() -> str | None:
    """Read the current panel position via DBus (Plasma shell).

    Returns:
        The panel location string (e.g. "top", "bottom", "left", "right"),
        or None on failure.
    """
    script = """
    var panels = panels();
    if (panels.length > 0) {
        print(panels[0].location);
    }
    """
    try:
        result = subprocess.run(
            [
                "qdbus",
                "org.kde.plasmashell",
                "/PlasmaShell",
                "org.kde.PlasmaShell.evaluateScript",
                script,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip() or None
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"  ⚠️  Could not read panel position: {e}")
        return None
