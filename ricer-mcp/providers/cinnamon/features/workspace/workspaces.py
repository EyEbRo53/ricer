"""Feature: workspaces (workspace)."""

from feature import Feature, FeatureType


class WorkspacesFeature(Feature):
    """Workspaces feature implementation for Cinnamon."""
    type = FeatureType.WORKSPACE

    def set(self, number: int) -> bool:
        """Set the number of workspaces via gsettings."""
        from utils.write.gsettings_writer import write_gsetting

        return write_gsetting(
            "org.cinnamon.desktop.wm.preferences", "num-workspaces", str(number)
        )

    def get(self) -> dict:
        """Return current workspaces setting as structured payload."""
        from utils.read.gsettings_reader import read_gsetting

        value = read_gsetting(
            "org.cinnamon.desktop.wm.preferences", "num-workspaces", "4"
        )
        try:
            num = int(value)
        except (ValueError, TypeError):
            num = 4

        return {
            "setting": "workspaces",
            "schema": "org.cinnamon.desktop.wm.preferences",
            "key": "num-workspaces",
            "values": {
                "number": num,
            },
            "error": (
                "Failed to read num-workspaces from gsettings."
                if value is None
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_workspaces(number: int) -> str:
            """Stage a workspace count change.

            Args:
                number: Number of workspaces (typically 1–12).

            Returns:
                JSON staging receipt with order number, script, and parameters.
            """
            import json

            receipt = changeset.add(
                description=f"Set number of workspaces to {number}",
                change_type="workspace",
                script="set_workspaces",
                parameters={"number": number},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("cinnamon://workspace/workspaces")
        def get_workspaces_resource() -> str:
            """Return the current number of workspaces."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = WorkspacesFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
