"""Feature: activities (workspace)."""

from feature import Feature
import subprocess

from feature import FeatureType

class ActivitiesFeature(Feature):
    type = FeatureType.WORKSPACE
    """Activities feature implementation using qdbus6."""

    def set(self, current_activity_uuid: str = None, new_activity_name: str = None) -> bool:
        """Set the current activity or create a new one."""
        success = True
        
        if new_activity_name is not None:
            try:
                subprocess.run(
                    ["qdbus6", "org.kde.ActivityManager", "/ActivityManager/Activities", "AddActivity", new_activity_name],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                success = False

        if current_activity_uuid is not None:
            try:
                subprocess.run(
                    ["qdbus6", "org.kde.ActivityManager", "/ActivityManager/Activities", "SetCurrentActivity", current_activity_uuid],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                success = False

        return success

    def get(self) -> dict:
        """Return a list of current activities."""
        activities = {}
        error = None
        try:
            result = subprocess.run(
                ["qdbus6", "org.kde.ActivityManager", "/ActivityManager/Activities", "ListActivities"],
                check=True,
                capture_output=True,
                text=True
            )
            uuids = [line.strip() for line in result.stdout.split('\n') if line.strip()]

            for uuid in uuids:
                name_res = subprocess.run(
                    ["qdbus6", "org.kde.ActivityManager", "/ActivityManager/Activities", "ActivityName", uuid],
                    check=True,
                    capture_output=True,
                    text=True
                )
                activities[uuid] = name_res.stdout.strip()
                
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            error = f"Failed to list activities: {e}"

        return {
            "setting": "activities",
            "values": {
                "activities": activities,
            },
            "error": error,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_activities(
            current_activity_uuid: str = None, new_activity_name: str = None
        ) -> str:
            """Stage settings to create a new activity or switch to an existing one by UUID."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set activity bindings: current_activity_uuid={current_activity_uuid}, "
                    f"new_activity_name={new_activity_name}"
                ),
                change_type="workspace",
                script="set_activities",
                parameters={
                    "current_activity_uuid": current_activity_uuid,
                    "new_activity_name": new_activity_name,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://workspace/activities")
        def get_activities_resource() -> str:
            """Return current activities."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = ActivitiesFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
