"""Feature: global display scaling (display)."""

from feature import Feature
from utils.write.kscreen_doctor import run_kscreen_doctor


class GlobalScalingFeature(Feature):
    """Global scaling feature implementation."""

    def set(self, scale_value: float) -> bool:
        """Apply global scaling via orchestrator (kscreen-doctor)."""
        return run_kscreen_doctor(f"output.1.scale.{scale_value}")

    def get(self) -> dict:
        """Return current global scaling as a structured payload."""
        from utils.kde_config_reader import read_kscreen_doctor

        info = read_kscreen_doctor()
        scale = info.get("scale") if info else None
        if not info:
            error = "Failed to read display state from kscreen-doctor."
        elif scale is None:
            error = "Display state read succeeded, but scale could not be parsed."
        else:
            error = None
        return {
            "setting": "global_scaling",
            "source": "kscreen-doctor",
            "value": scale,
            "output": info if info else None,
            "error": error,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_global_scaling(scale_value: float) -> str:
            """Stage a global UI scaling change."""
            import json

            receipt = changeset.add(
                description=f"Set global scaling to {scale_value}×",
                change_type="display",
                script="set_global_scaling",
                parameters={"scale_value": scale_value},
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://display/global-scaling")
        def get_global_scaling_resource() -> str:
            """Return the current global UI scaling factor."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = GlobalScalingFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
