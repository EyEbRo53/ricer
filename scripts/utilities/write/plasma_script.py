#!/usr/bin/env python3
"""Execute Plasma shell scripts via qdbus."""
import subprocess


def run_plasma_script(script: str, description: str = "Plasma script") -> bool:
    """Execute a Plasma shell script via qdbus.

    Args:
        script: JavaScript code to evaluate in PlasmaShell.
        description: Human-readable description for logging.

    Returns:
        True on success, False on failure.
    """
    try:
        subprocess.run(
            [
                "qdbus",
                "org.kde.plasmashell",
                "/PlasmaShell",
                "org.kde.PlasmaShell.evaluateScript",
                script,
            ],
            check=True,
            capture_output=True,
        )
        print(f"  ✓ {description}")
        return True
    except FileNotFoundError:
        print(f"  ❌ qdbus not found – cannot run {description}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Error running {description}: {e}")
        return False
