"""Feature: mouse settings (input)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs

from feature import FeatureType

class MouseSettingsFeature(Feature):
    type = FeatureType.INPUT
    """Mouse settings feature implementation."""

    def set(self, acceleration_profile: str = None, pointer_acceleration: float = None) -> bool:
        """Configure mouse acceleration profile (flat/adaptive) and speed."""
        configs = []
        if acceleration_profile is not None:
            configs.append(("kcminputrc", "Mouse", "AccelerationProfile", acceleration_profile))
        if pointer_acceleration is not None:
            configs.append(("kcminputrc", "Mouse", "PointerAcceleration", str(pointer_acceleration)))

        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current mouse settings."""
        from utils.read.kreadconfig import read_kde_config

        accel = read_kde_config("kcminputrc", "Mouse", "PointerAcceleration", "0")
        try:
            accel_val = float(accel)
        except ValueError:
            accel_val = 0.0

        return {
            "setting": "mouse_settings",
            "values": {
                "acceleration_profile": read_kde_config("kcminputrc", "Mouse", "AccelerationProfile", "adaptive"),
                "pointer_acceleration": accel_val,
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_mouse_settings(
            acceleration_profile: str = None, pointer_acceleration: float = None
        ) -> str:
            """Stage mouse settings like acceleration profile and speed."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set mouse settings: profile={acceleration_profile}, "
                    f"speed={pointer_acceleration}"
                ),
                change_type="input",
                script="set_mouse_settings",
                parameters={
                    "acceleration_profile": acceleration_profile,
                    "pointer_acceleration": pointer_acceleration,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://input/mouse-settings")
        def get_mouse_settings_resource() -> str:
            """Return current mouse settings."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = MouseSettingsFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
