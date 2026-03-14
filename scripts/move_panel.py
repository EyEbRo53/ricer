#!/usr/bin/env python3
"""Move KDE Plasma panel to a given edge."""
from utilities.write.plasma_script import run_plasma_script

_VALID_POSITIONS = {"top", "bottom", "left", "right"}


def move_panel(position: str) -> bool:
    """Move the first Plasma panel via orchestrator.

    Args:
        position: One of "top", "bottom", "left", "right".

    Returns:
        True on success, False on failure.
    """
    position = position.lower().strip()
    if position not in _VALID_POSITIONS:
        print(f"  ❌ Invalid position: {position}. Must be one of {_VALID_POSITIONS}")
        return False

    script = f"""
    var panels = panels();
    if (panels.length > 0) {{
        var panel = panels[0];
        panel.location = "{position}";
    }}
    """
    return run_plasma_script(script, f"Panel moved to: {position}")


