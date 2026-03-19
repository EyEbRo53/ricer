"""Feature: panel position (display)."""

from feature import Feature
from utils.write.plasma_script import run_plasma_script

_VALID_POSITIONS = {"top", "bottom", "left", "right"}


class PanelPositionFeature(Feature):
    """Panel position feature implementation."""

    def execute(self, position: str) -> bool:
        """Move the first Plasma panel via orchestrator."""
        position = position.lower().strip()
        if position not in _VALID_POSITIONS:
            print(f"  ❌ Invalid position: {position}. Must be one of {_VALID_POSITIONS}")
            return False

        script = f"""
    var panels = panels();
    if (panels.length > 0) {{
        var panel = panels[0];
        panel.location = \"{position}\";
    }}
    """
        return run_plasma_script(script, f"Panel moved to: {position}")

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def move_panel(position: str) -> str:
            """Stage a panel (taskbar) position change."""
            import json

            receipt = changeset.add(
                description=f"Move panel to {position}",
                change_type="display",
                script="move_panel",
                parameters={"position": position},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://display/panel-position")
        def get_panel_position() -> str:
            """Return the current panel (taskbar) position."""
            import json
            from utils.kde_config_reader import read_panel_position

            position = read_panel_position()
            return json.dumps(
                {
                    "setting": "panel_position",
                    "source": "dbus (org.kde.plasmashell)",
                    "value": position,
                    "error": (
                        "Failed to read panel position from DBus (org.kde.plasmashell)."
                        if position is None
                        else None
                    ),
                },
                indent=2,
            )


feature = PanelPositionFeature()


def move_panel(position: str) -> bool:
    """Script entrypoint for confirmed panel position changes."""
    return feature.execute(position=position)


def register(mcp, changeset):
    feature.register(mcp, changeset)
