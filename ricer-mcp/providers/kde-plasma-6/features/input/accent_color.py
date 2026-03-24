"""Feature: accent color (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config

class AccentColorFeature(Feature):
    type = FeatureType.INPUT

    def set(self, color: str, use_custom: bool = True) -> bool:
        """Set KDE Plasma accent color via kwriteconfig6."""
        success = write_kde_config(
            "kdeglobals", "General", "AccentColor", color
        )
        if success:
            success = write_kde_config(
                "kdeglobals", "General", "UseAccentColor", "true" if use_custom else "false"
            )
        return success

    def get(self) -> dict:
        """Return current accent color as a structured payload."""
        color = read_kde_config("kdeglobals", "General", "AccentColor", "")
        use_custom = read_kde_config("kdeglobals", "General", "UseAccentColor", "false")
        return {
            "setting": "accent_color",
            "file": "kdeglobals",
            "group": "General",
            "key": "AccentColor",
            "value": color,
            "use_custom": use_custom == "true",
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_accent_color(color: str, use_custom: bool = True) -> str:
            """Stage an accent color change."""
            import json
            receipt = changeset.add(
                "accent_color", {"color": color, "use_custom": use_custom}
            )
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_accent_color() -> dict:
            """Return current accent color setting."""
            return self.get()
