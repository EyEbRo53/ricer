"""Feature: application launch feedback (workspace)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_config

from feature import FeatureType

class LaunchFeedbackFeature(Feature):
    type = FeatureType.WORKSPACE
    """Launch feedback feature implementation."""

    def set(self, feedback_type: str) -> bool:
        """Set application launch feedback (e.g., None, BusyCursor, Bouncing)."""
        return write_kde_config("plasmarc", "LaunchFeedback", "LaunchFeedback", feedback_type)

    def get(self) -> dict:
        """Return current launch feedback setting."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "launch_feedback",
            "values": {
                "feedback_type": read_kde_config("plasmarc", "LaunchFeedback", "LaunchFeedback", "BusyCursor"),
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_launch_feedback(feedback_type: str) -> str:
            """Stage application launch feedback style."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set launch feedback to: {feedback_type}"
                ),
                change_type="workspace",
                script="set_launch_feedback",
                parameters={
                    "feedback_type": feedback_type,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://workspace/launch-feedback")
        def get_launch_feedback_resource() -> str:
            """Return current launch feedback setting."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = LaunchFeedbackFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
