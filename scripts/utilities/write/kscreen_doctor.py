#!/usr/bin/env python3
"""KDE display scaling via kscreen-doctor."""
import subprocess


def run_kscreen_doctor(output_spec: str) -> bool:
    """Run kscreen-doctor with the given output spec.

    Args:
        output_spec: e.g. "output.1.scale.1.25"

    Returns:
        True on success, False on failure.
    """
    try:
        subprocess.run(
            ["kscreen-doctor", output_spec],
            check=True,
            capture_output=True,
        )
        print(f"  ✓ kscreen-doctor {output_spec}")
        return True
    except FileNotFoundError:
        print("  ❌ kscreen-doctor not found – skipping")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  kscreen-doctor error: {e}")
        return False
