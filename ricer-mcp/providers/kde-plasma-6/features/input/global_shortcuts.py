"""Feature: global shortcuts (input)."""

from feature import Feature
from utils.write.kwriteconfig import write_kde_config

from feature import FeatureType

class GlobalShortcutsFeature(Feature):
    type = FeatureType.INPUT
    """Global shortcuts feature implementation."""

    def set(self, component: str, action: str, shortcut: str) -> bool:
        """Set a global keyboard shortcut.
        
        To clear a shortcut, pass shortcut='none'
        """
        value = f"{shortcut},none,{action}"
        return write_kde_config("kglobalshortcutsrc", component, action, value)

    def get(self) -> dict:
        """Return generic structure since we cannot enumerate all easily."""
        return {
            "setting": "global_shortcuts",
            "error": "Reading all global shortcuts is not fully supported via kreadconfig6 natively without iteration. Provide component and action.",
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_global_shortcut(component: str, action: str, shortcut: str) -> str:
            """Stage a global shortcut for a specific component and action."""
            import json

            parameters = {
                "component": component,
                "action": action,
                "shortcut": shortcut,
            }

            receipt = changeset.add(
                description=(
                    f"Set global shortcut for '{component}' -> '{action}' to '{shortcut}'"
                ),
                change_type="input",
                script="set_global_shortcut",
                parameters=parameters,
            )
            return json.dumps(receipt, indent=2)

    def register_resource(self, mcp) -> None:
        pass # Skipping resource since we can't easily list all


feature = GlobalShortcutsFeature()


def register(mcp, changeset):
    feature.register(mcp, changeset)
