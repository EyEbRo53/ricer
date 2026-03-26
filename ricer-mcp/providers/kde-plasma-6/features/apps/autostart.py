"""Feature: autostart applications (apps)."""

import os
from feature import Feature

from feature import FeatureType

class AutostartFeature(Feature):
    type = FeatureType.APPS
    """Autostart application feature implementation."""

    def set(self, app_name: str, command: str, hidden: bool = False) -> bool:
        """Add an application or script to KDE autostart."""
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        
        # safe filename
        safe_name = "".join(c if c.isalnum() else "_" for c in app_name).strip("_")
        desktop_file = os.path.join(autostart_dir, f"{safe_name}.desktop")
        
        content = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec={command}
Hidden={str(hidden).lower()}
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
        try:
            with open(desktop_file, "w") as f:
                f.write(content)
            return True
        except Exception:
            return False

    def get(self) -> dict:
        """Return generic info because parsing all autostart is complex."""
        return {
            "setting": "autostart",
            "error": "Listing all autostart items is not fully supported via simple read.",
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def add_autostart_app(
            app_name: str, command: str, hidden: bool = False
        ) -> str:
            """Stage an application to be added to KDE autostart."""
            import json

            parameters = {
                "app_name": app_name,
                "command": command,
                "hidden": hidden,
            }

            receipt = changeset.add(
                description=(
                    f"Add autostart app '{app_name}' running '{command}'"
                ),
                change_type="apps",
                script="add_autostart_app",
                parameters=parameters,
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        pass # Skipping resource


feature = AutostartFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
