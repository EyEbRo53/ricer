"""Generic read-only resource for available Cinnamon desktop assets."""

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


def _list_gtk_themes() -> list[str]:
    """Return installed GTK themes (directories containing a gtk-3.0/ subdir)."""
    roots = [
        "~/.themes",
        "/usr/share/themes",
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
                # A valid GTK theme has a gtk-3.0 or gtk-4.0 subdir
                if os.path.isdir(os.path.join(theme_dir, "gtk-3.0")) or \
                   os.path.isdir(os.path.join(theme_dir, "gtk-4.0")):
                    found.add(entry)
        except OSError:
            continue

    return sorted(found)


def _list_cinnamon_themes() -> list[str]:
    """Return installed Cinnamon themes (directories containing a cinnamon/ subdir)."""
    roots = [
        "~/.themes",
        "/usr/share/themes",
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
                if os.path.isdir(os.path.join(theme_dir, "cinnamon")):
                    found.add(entry)
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
    """Build a generic read-only catalog of available Cinnamon desktop assets."""
    catalog = {
        "gtk_themes": _list_gtk_themes(),
        "cinnamon_themes": _list_cinnamon_themes(),
        "icon_themes": _list_icon_themes(),
        "cursor_themes": _list_cursor_themes(),
        "font_families": _list_font_families(),
    }

    return {
        "resource": "cinnamon://resources/catalog",
        "description": (
            "Installed desktop assets discovered from common Cinnamon/GTK/XDG paths "
            "and fontconfig. Use these names when staging appearance changes."
        ),
        "counts": {k: len(v) for k, v in catalog.items()},
        "catalog": catalog,
    }


def register(mcp) -> None:
    """Register generic provider resource(s) for desktop asset discovery."""

    @mcp.resource("cinnamon://resources/catalog")
    def get_resource_catalog() -> str:
        """Return available GTK themes, Cinnamon themes, icon themes, cursor themes, and fonts."""
        return json.dumps(build_catalog(), indent=2)
