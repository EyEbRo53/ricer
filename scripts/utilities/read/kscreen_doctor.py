#!/usr/bin/env python3
"""Query display configuration via kscreen-doctor."""
import subprocess
import re


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
        print("  ❌ kscreen-doctor not found – cannot read display info")
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
