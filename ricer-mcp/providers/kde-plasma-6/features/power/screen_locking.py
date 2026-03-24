"""Feature: screen locking and screensaver (power)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_configs

from feature import FeatureType

class ScreenLockingFeature(Feature):
    type = FeatureType.POWER
    """Screen locking and screensaver feature implementation."""

    def set(self, lock_grace: int = None, auto_lock: bool = None, timeout: int = None, theme: str = None) -> bool:
        """Configure screen locking and screensaver."""
        configs = []
        if lock_grace is not None:
            configs.append(("kscreenlockerrc", "Greeter", "lockGrace", str(lock_grace)))
        if auto_lock is not None:
            configs.append(("kscreenlockerrc", "Daemon", "Autolock", str(auto_lock).lower()))
        if timeout is not None:
            configs.append(("kscreenlockerrc", "Daemon", "Timeout", str(timeout)))
        if theme is not None:
            configs.append(("kscreensaverrc", "ScreenSaver", "Theme", theme))
        
        if not configs:
            return True
        return write_kde_configs(configs)

    def get(self) -> dict:
        """Return current screen locking settings."""
        from utils.read.kreadconfig import read_kde_config

        return {
            "setting": "screen_locking",
            "values": {
                "lock_grace": read_kde_config("kscreenlockerrc", "Greeter", "lockGrace", "0"),
                "auto_lock": read_kde_config("kscreenlockerrc", "Daemon", "Autolock", "false") == "true",
                "timeout": read_kde_config("kscreenlockerrc", "Daemon", "Timeout", "0"),
                "theme": read_kde_config("kscreensaverrc", "ScreenSaver", "Theme", ""),
            },
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_screen_locking(
            lock_grace: int = None, auto_lock: bool = None, timeout: int = None, theme: str = None
        ) -> str:
            """Stage screen locking and screensaver settings."""
            import json

            receipt = changeset.add(
                description=(
                    f"Set screen locking: lock_grace={lock_grace}, auto_lock={auto_lock}, "
                    f"timeout={timeout}, theme={theme}"
                ),
                change_type="power",
                script="set_screen_locking",
                parameters={
                    "lock_grace": lock_grace,
                    "auto_lock": auto_lock,
                    "timeout": timeout,
                    "theme": theme,
                },
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        @mcp.resource("plasma://power/screen-locking")
        def get_screen_locking_resource() -> str:
            """Return current screen locking settings."""
            import json

            return json.dumps(feature.get(), indent=2)


feature = ScreenLockingFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
