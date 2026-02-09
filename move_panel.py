#!/usr/bin/env python3
import subprocess

plasma_script = """
var panels = panels();
if (panels.length > 0) {
    var panel = panels[0]; // first panel
    panel.location = "right";
}
"""

subprocess.run(
    [
        "qdbus",
        "org.kde.plasmashell",
        "/PlasmaShell",
        "org.kde.PlasmaShell.evaluateScript",
        plasma_script,
    ]
)
