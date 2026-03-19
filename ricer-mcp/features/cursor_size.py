"""Feature: cursor size (input)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_config
from utils.reload.reconfigure_kwin import reconfigure_kwin


class CursorSizeFeature(Feature):
    """Cursor size feature implementation."""

    def execute(self, size: int) -> bool:
        """Configure cursor size via orchestrator and apply immediately."""
        success = write_kde_config("kcminputrc", "Mouse", "cursorSize", str(size))
        if success:
            reconfigure_kwin()
        return success

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_cursor_size(size: int) -> str:
            """Stage a cursor size change."""
            import json

            receipt = changeset.add(
                description=f"Set cursor size to {size}px",
                change_type="input",
                script="set_cursor_size",
                parameters={"size": size},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://input/cursor-size")
        def get_cursor_size() -> str:
            """Return the current cursor size in pixels."""
            import json
            from utils.kde_config_reader import read_kde_config

            value = read_kde_config("kcminputrc", "Mouse", "cursorSize", "24")
            parsed_value = int(value) if value and value.isdigit() else value
            return json.dumps(
                {
                    "setting": "cursor_size",
                    "file": "kcminputrc",
                    "group": "Mouse",
                    "key": "cursorSize",
                    "value": parsed_value,
                    "unit": "px",
                    "error": (
                        "Failed to read kcminputrc [Mouse] cursorSize via kreadconfig6."
                        if value is None
                        else None
                    ),
                },
                indent=2,
            )


feature = CursorSizeFeature()


def set_cursor_size(size: int) -> bool:
    """Script entrypoint for confirmed cursor size changes."""
    return feature.execute(size=size)


def register(mcp, changeset):
    feature.register(mcp, changeset)
