#!/usr/bin/env python3
"""Query display configuration via kscreen-doctor."""
import subprocess
import re
import shutil


_ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")


def read_kscreen_doctor() -> dict | None:
    """Query kscreen-doctor for current output configuration.

    Parses ``kscreen-doctor --outputs`` (or ``-o``) and extracts the first
    output's scale and other useful properties.

    Returns:
        A dict with keys like ``name``, ``scale``, ``resolution``, ``enabled``
        for the first output, or None if the command fails.
    """
    executable = shutil.which("kscreen-doctor") or "kscreen-doctor"
    commands = [
        [executable, "-o"],
        [executable, "--outputs"],
    ]
    errors: list[str] = []

    for cmd in commands:
        try:
            result = subprocess.run(
                cmd,
                check=False,
                capture_output=True,
                text=True,
            )

            # Some versions emit useful data on stderr.
            raw = (result.stdout or "") + "\n" + (result.stderr or "")
            parsed = _parse_kscreen_output(raw)
            if parsed:
                return parsed

            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                errors.append(f"{' '.join(cmd)} -> {result.returncode}: {stderr}")
        except FileNotFoundError:
            print("  ❌ kscreen-doctor not found – cannot read display info")
            return None

    if errors:
        print("  ⚠️  kscreen-doctor read failed:")
        for err in errors:
            print(f"     - {err}")
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
    clean = _ANSI_ESCAPE_RE.sub("", raw)

    # Output name
    m = re.search(r"Output:\s+\d+\s+(\S+)", clean)
    if m:
        info["name"] = m.group(1)

    # Enabled / connected
    info["enabled"] = "enabled" in clean.lower()
    info["connected"] = "connected" in clean.lower()

    # Scale
    m = re.search(r"Scale:\s*([\d.]+)", clean, re.IGNORECASE)
    if m:
        info["scale"] = float(m.group(1))

    # Resolution (current mode, often marked with *)
    m = re.search(r"(\d{3,5}x\d{3,5}).*?\*", clean)
    if m:
        info["resolution"] = m.group(1)

    return info
