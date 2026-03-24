"""Feature: virtual desktops (workspace)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs

from feature import FeatureType

class VirtualDesktopsFeature(Feature):
    type = FeatureType.WORKSPACE
    """Virtual desktops feature implementation."""

    def set(self, number: int = None, names: dict[str, str] = None) -> bool:
        """Set number of virtual desktops and optionally rename them.
        
        names: Mapping of index (starts at 1) to desktop name.
        """
        configs = []
        if number is not None:
            configs.append(("kwinrc", "Desktops", "Number", str(number)))
        
        if names:
            for idx, name in names.items():
                configs.append(("kwinrc", "Desktops", f"Name_{idx}", name))

        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current virtual desktops settings."""
        from utils.read.kreadconfig import read_kde_config

        num_str = read_kde_config("kwinrc", "Desktops", "Number", "1")
        try:
            num = int(num_str)
        except ValueError:
            num = 1

        names = {}
        for i in range(1, num + 1):
            names[str(i)] = read_kde_config("kwinrc", "Desktops", f"Name_{i}", f"Desktop {i}")

        return {
            "setting": "virtual_desktops",
            "values": {
                "number": num,
                "names": names,
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_virtual_desktops(
            number: int = None, names: dict = None
        ) -> str:
            """Stage virtual desktops settings."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set virtual desktops: number={number}, names={names}"
                ),
                change_type="workspace",
                script="set_virtual_desktops",
                parameters={
                    "number": number,
                    "names": names,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://workspace/virtual-desktops")
        def get_virtual_desktops_resource() -> str:
            """Return current virtual desktops settings."""
            import json

            return json.dumps(feature.get(), indent=2)


feature = VirtualDesktopsFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
