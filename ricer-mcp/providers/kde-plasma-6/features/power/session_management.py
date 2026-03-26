"""Feature: session management (power)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs

from feature import FeatureType

class SessionManagementFeature(Feature):
    type = FeatureType.POWER
    """Session management feature implementation."""

    def set(self, login_mode: int = None, auto_save_session: bool = None) -> bool:
        """Configure session login mode and auto-save."""
        configs = []
        if login_mode is not None:
            configs.append(("ksmserverrc", "General", "loginMode", str(login_mode)))
        if auto_save_session is not None:
            configs.append(("ksmserverrc", "General", "autoSaveSession", str(auto_save_session).lower()))
        
        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current session settings."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "session_management",
            "values": {
                "login_mode": read_kde_config("ksmserverrc", "General", "loginMode", "0"),
                "auto_save_session": read_kde_config("ksmserverrc", "General", "autoSaveSession", "false") == "true",
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_session_management(
            login_mode: int = None, auto_save_session: bool = None
        ) -> str:
            """Stage session management settings."""
            import json

            parameters = {k: v for k, v in {"login_mode": login_mode, "auto_save_session": auto_save_session}.items() if v is not None}

            receipt = changeset.add(
                description=(
                    f"Set session management: {', '.join(f'{k}={v}' for k, v in parameters.items())}"
                ),
                change_type="power",
                script="set_session_management",
                parameters=parameters,
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://power/session-management")
        def get_session_management_resource() -> str:
            """Return current session settings."""
            import json
            return json.dumps(feature.get(), indent=2)


feature = SessionManagementFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
