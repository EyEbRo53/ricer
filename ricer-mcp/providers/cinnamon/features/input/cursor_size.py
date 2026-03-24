"""Feature: cursor size (input)."""

from feature import Feature, FeatureType


class CursorSizeFeature(Feature):
    """Cursor size feature implementation for Cinnamon."""
    type = FeatureType.INPUT

    def set(self, size: int) -> bool:
        """Set Cinnamon cursor size via gsettings."""
        from utils.write.gsettings_writer import write_gsetting

        return write_gsetting(
            "org.cinnamon.desktop.interface", "cursor-size", str(size)
        )

    def get(self) -> dict:
        """Return current cursor size as structured payload."""
        from utils.read.gsettings_reader import read_gsetting

        value = read_gsetting("org.cinnamon.desktop.interface", "cursor-size", "24")
        parsed_value = int(value) if value and str(value).isdigit() else value
        return {
            "setting": "cursor_size",
            "schema": "org.cinnamon.desktop.interface",
            "key": "cursor-size",
            "value": parsed_value,
            "unit": "px",
            "error": (
                "Failed to read cursor-size from gsettings."
                if value is None
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_cursor_size(size: int) -> str:
            """Stage a cursor size change.

            Args:
                size: Cursor size in pixels. Common values: 24, 32, 48, 64.

            Returns:
                JSON staging receipt with order number, script, and parameters.
            """
            import json

            receipt = changeset.add(
                description=f"Set cursor size to {size}px",
                change_type="input",
                script="set_cursor_size",
                parameters={"size": size},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("cinnamon://input/cursor-size")
        def get_cursor_size_resource() -> str:
            """Return the current cursor size in pixels."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = CursorSizeFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
