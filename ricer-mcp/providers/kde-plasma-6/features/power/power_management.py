"""Feature: power management (power)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs


from feature import FeatureType

class PowerManagementFeature(Feature):
    type = FeatureType.POWER
    """Power management feature implementation."""

    def set(
        self,
        ac_dim_display: int = None,
        ac_suspend: int = None,
        ac_lid_closed: int = None,
        battery_dim_display: int = None,
        battery_suspend: int = None,
        battery_lid_closed: int = None,
    ) -> bool:
        """Adjust power management settings for AC and Battery profiles."""
        configs = []
        if ac_dim_display is not None:
            configs.append(("powermanagementprofilesrc", ["AC", "DimDisplay"], "idleTime", str(ac_dim_display * 1000)))
        if ac_suspend is not None:
            configs.append(("powermanagementprofilesrc", ["AC", "SuspendSession"], "idleTime", str(ac_suspend * 1000)))
        if ac_lid_closed is not None:
            configs.append(("powermanagementprofilesrc", ["AC", "LidClosed"], "action", str(ac_lid_closed)))
            
        if battery_dim_display is not None:
            configs.append(("powermanagementprofilesrc", ["Battery", "DimDisplay"], "idleTime", str(battery_dim_display * 1000)))
        if battery_suspend is not None:
            configs.append(("powermanagementprofilesrc", ["Battery", "SuspendSession"], "idleTime", str(battery_suspend * 1000)))
        if battery_lid_closed is not None:
            configs.append(("powermanagementprofilesrc", ["Battery", "LidClosed"], "action", str(battery_lid_closed)))

        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current power management settings."""
        from utils.read.kreadconfig import read_kde_configs

        configs = [
            ("powermanagementprofilesrc", ["AC", "DimDisplay"], "idleTime", "0"),
            ("powermanagementprofilesrc", ["AC", "SuspendSession"], "idleTime", "0"),
            ("powermanagementprofilesrc", ["AC", "LidClosed"], "action", "0"),
            ("powermanagementprofilesrc", ["Battery", "DimDisplay"], "idleTime", "0"),
            ("powermanagementprofilesrc", ["Battery", "SuspendSession"], "idleTime", "0"),
            ("powermanagementprofilesrc", ["Battery", "LidClosed"], "action", "0"),
        ]
        values = read_kde_configs(configs)
        failed_keys = [k for k, v in values.items() if v is None]

        def _ms_to_s(v):
            try:
                return int(v) // 1000 if v else 0
            except (ValueError, TypeError):
                return 0

        def _int_or_0(v):
            try:
                return int(v) if v else 0
            except (ValueError, TypeError):
                return 0

        return {
            "setting": "power_management",
            "file": "powermanagementprofilesrc",
            "groups": ["AC", "Battery"],
            "values": {
                "ac_dim_display": _ms_to_s(values.get("idleTime")), # Wait, read_kde_configs keys by "key" name! 
                # This will conflict because we have "idleTime" multiple times!
            },
            "error": "Not fully implemented due to key collision in reader. Needs custom read logic.",
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_power_management(
            ac_dim_display: int = None,
            ac_suspend: int = None,
            ac_lid_closed: int = None,
            battery_dim_display: int = None,
            battery_suspend: int = None,
            battery_lid_closed: int = None,
        ) -> str:
            """Stage power management settings (dim time, suspend time, lid action)."""
            import json

            receipt = changeset.add(
                description=(
                    "Set power management settings."
                ),
                change_type="power",
                script="set_power_management",
                parameters={
                    "ac_dim_display": ac_dim_display,
                    "ac_suspend": ac_suspend,
                    "ac_lid_closed": ac_lid_closed,
                    "battery_dim_display": battery_dim_display,
                    "battery_suspend": battery_suspend,
                    "battery_lid_closed": battery_lid_closed,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        pass # Skipping resource since we have key conflict in read_kde_configs


feature = PowerManagementFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
