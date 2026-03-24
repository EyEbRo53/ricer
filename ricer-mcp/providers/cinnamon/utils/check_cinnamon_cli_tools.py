#!/usr/bin/env python3
"""Check that required CLI tools for the Cinnamon provider are available."""
import shutil


_REQUIRED_TOOLS = ("gsettings", "dconf")


def check_cinnamon_cli_tools() -> dict[str, bool]:
    """Return a mapping of tool-name → available for each required tool.

    Returns:
        Dict like ``{"gsettings": True, "dconf": True}``.
    """
    return {tool: shutil.which(tool) is not None for tool in _REQUIRED_TOOLS}


def ensure_cinnamon_cli_tools() -> None:
    """Raise RuntimeError if any required CLI tool is missing."""
    status = check_cinnamon_cli_tools()
    missing = [t for t, ok in status.items() if not ok]
    if missing:
        raise RuntimeError(
            f"Cinnamon provider requires these CLI tools: {', '.join(missing)}. "
            "Please install the corresponding packages."
        )
