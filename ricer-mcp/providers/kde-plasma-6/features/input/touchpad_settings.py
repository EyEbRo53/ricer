"""Feature: touchpad settings (input)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs


from feature import FeatureType

class TouchpadSettingsFeature(Feature):
    type = FeatureType.INPUT
    """Touchpad settings feature implementation."""

    def set(self, acceleration: float, speed: float, deceleration: float) -> bool:
        """Adjust touchpad sensitivity, acceleration and deceleration."""
        configs = [
            ("kcminputrc", "Touchpad", "Acceleration", str(acceleration)),
            ("kcminputrc", "Touchpad", "Speed", str(speed)),
            ("kcminputrc", "Touchpad", "Deceleration", str(deceleration)),
        ]
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current touchpad settings as a structured payload."""
        from utils.kde_config_reader import read_kde_configs

        configs = [
            ("kcminputrc", "Touchpad", "Acceleration", "0"),
            ("kcminputrc", "Touchpad", "Speed", "0"),
            ("kcminputrc", "Touchpad", "Deceleration", "0"),
        ]
        values = read_kde_configs(configs)
        failed_keys = [k for k, v in values.items() if v is None]

        def _float_or_raw(v):
            try:
                return float(v) if v else v
            except (ValueError, TypeError):
                return v

        return {
            "setting": "touchpad_settings",
            "file": "kcminputrc",
            "group": "Touchpad",
            "values": {
                "acceleration": _float_or_raw(values.get("Acceleration")),
                "speed": _float_or_raw(values.get("Speed")),
                "deceleration": _float_or_raw(values.get("Deceleration")),
            },
            "error": (
                "Failed to read kcminputrc touchpad keys via kreadconfig6: "
                + ", ".join(failed_keys)
                if failed_keys
                else None
            ),
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_touchpad_settings(
            acceleration: float, speed: float, deceleration: float
        ) -> str:
            """Stage touchpad sensitivity and acceleration settings."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set touchpad settings: acceleration={acceleration}, "
                    f"speed={speed}, deceleration={deceleration}"
                ),
                change_type="input",
                script="set_touchpad_settings",
                parameters={
                    "acceleration": acceleration,
                    "speed": speed,
                    "deceleration": deceleration,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://input/touchpad-settings")
        def get_touchpad_settings_resource() -> str:
            """Return current touchpad acceleration, speed, and deceleration."""
            import json

            return json.dumps(feature.get(), indent=2)


feature = TouchpadSettingsFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
