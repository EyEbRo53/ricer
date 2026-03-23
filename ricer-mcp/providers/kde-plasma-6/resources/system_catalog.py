"""Generic read-only resource for available desktop assets."""

from __future__ import annotations

import json
import os
import subprocess


def _list_dir_names(paths: list[str]) -> list[str]:
    """Collect unique directory names from a list of roots."""
    found: set[str] = set()
    for root in paths:
        expanded = os.path.expanduser(root)
        if not os.path.isdir(expanded):
            continue

        try:
            for entry in os.listdir(expanded):
                full = os.path.join(expanded, entry)
                if os.path.isdir(full):
                    found.add(entry)
        except OSError:
            continue

    return sorted(found)


def _list_color_schemes() -> list[str]:
    """Return installed KDE color scheme names (without .colors)."""
    roots = [
        "~/.local/share/color-schemes",
        "/usr/share/color-schemes",
    ]
    found: set[str] = set()
    for root in roots:
        expanded = os.path.expanduser(root)
        if not os.path.isdir(expanded):
            continue

        try:
            for entry in os.listdir(expanded):
                if entry.endswith(".colors"):
                    found.add(entry[:-7])
        except OSError:
            continue

    return sorted(found)


def _list_icon_themes() -> list[str]:
    """Return icon themes that expose an index.theme manifest."""
    roots = [
        "~/.icons",
        "~/.local/share/icons",
        "/usr/share/icons",
    ]
    found: set[str] = set()
    for root in roots:
        expanded = os.path.expanduser(root)
        if not os.path.isdir(expanded):
            continue

        try:
            for entry in os.listdir(expanded):
                theme_dir = os.path.join(expanded, entry)
                if not os.path.isdir(theme_dir):
                    continue
                if os.path.isfile(os.path.join(theme_dir, "index.theme")):
                    found.add(entry)
        except OSError:
            continue

    return sorted(found)


def _list_cursor_themes() -> list[str]:
    """Return cursor themes by detecting 'cursors' directories."""
    roots = [
        "~/.icons",
        "~/.local/share/icons",
        "/usr/share/icons",
    ]
    found: set[str] = set()
    for root in roots:
        expanded = os.path.expanduser(root)
        if not os.path.isdir(expanded):
            continue

        try:
            for entry in os.listdir(expanded):
                theme_dir = os.path.join(expanded, entry)
                if not os.path.isdir(theme_dir):
                    continue
                if os.path.isdir(os.path.join(theme_dir, "cursors")):
                    found.add(entry)
        except OSError:
            continue

    return sorted(found)


def _list_font_families(limit: int = 500) -> list[str]:
    """Return font family names via fc-list, capped to keep payload bounded."""
    try:
        result = subprocess.run(
            ["fc-list", ":", "family"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    names: set[str] = set()
    for line in result.stdout.splitlines():
        for part in line.split(","):
            value = part.strip()
            if value:
                names.add(value)

    return sorted(names)[:limit]


def build_catalog() -> dict:
    """Build a generic read-only catalog of available desktop assets."""
    catalog = {
        "color_schemes": _list_color_schemes(),
        "plasma_themes": _list_dir_names(
            [
                "~/.local/share/plasma/desktoptheme",
                "/usr/share/plasma/desktoptheme",
            ]
        ),
        "look_and_feel_packages": _list_dir_names(
            [
                "~/.local/share/plasma/look-and-feel",
                "/usr/share/plasma/look-and-feel",
            ]
        ),
        "icon_themes": _list_icon_themes(),
        "cursor_themes": _list_cursor_themes(),
        "font_families": _list_font_families(),
    }

    return {
        "resource": "plasma://resources/catalog",
        "description": (
            "Installed desktop assets discovered from common KDE/XDG paths "
            "and fontconfig. Use these names when staging appearance changes."
        ),
        "counts": {k: len(v) for k, v in catalog.items()},
        "catalog": catalog,
    }


def register(mcp) -> None:
    """Register generic provider resource(s) for desktop asset discovery."""

    @mcp.resource("plasma://resources/catalog")
    def get_resource_catalog() -> str:
        """Return available color schemes, fonts, icon themes, and KDE themes."""
        return json.dumps(build_catalog(), indent=2)
