"""Feature: bluetooth (input/network)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs

from feature import FeatureType

class BluetoothFeature(Feature):
    type = FeatureType.INPUT
    """Bluetooth settings feature implementation."""

    def set(self, auto_power_on: bool = None, discoverable: bool = None) -> bool:
        """Configure bluetooth auto power on and discoverability."""
        configs = []
        if auto_power_on is not None:
            configs.append(("bluedevilglobalrc", "Bluetooth", "autoPowerOn", str(auto_power_on).lower()))
        if discoverable is not None:
            configs.append(("bluedevilglobalrc", "Bluetooth", "discoverable", str(discoverable).lower()))

        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current bluetooth settings."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "bluetooth",
            "values": {
                "auto_power_on": read_kde_config("bluedevilglobalrc", "Bluetooth", "autoPowerOn", "false") == "true",
                "discoverable": read_kde_config("bluedevilglobalrc", "Bluetooth", "discoverable", "false") == "true",
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_bluetooth_settings(
            auto_power_on: bool = None, discoverable: bool = None
        ) -> str:
            """Stage bluetooth settings like auto-power and discoverability."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set bluetooth: auto_power_on={auto_power_on}, discoverable={discoverable}"
                ),
                change_type="input",
                script="set_bluetooth_settings",
                parameters={
                    "auto_power_on": auto_power_on,
                    "discoverable": discoverable,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://input/bluetooth")
        def get_bluetooth_resource() -> str:
            """Return current bluetooth settings."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = BluetoothFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
