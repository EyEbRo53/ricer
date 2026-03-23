"""Feature: compositing backend (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
from utils.reload.reconfigure_kwin import reconfigure_kwin

class CompositingBackendFeature(Feature):
    type = FeatureType.INPUT

    def set(self, backend: str) -> bool:
        success = write_kde_config("kwinrc", "Compositing", "Backend", backend)
        if success:
            reconfigure_kwin()
        return success

    def get(self) -> dict:
        value = read_kde_config("kwinrc", "Compositing", "Backend", "OpenGL")
        return {
            "setting": "compositing_backend",
            "file": "kwinrc",
            "group": "Compositing",
            "key": "Backend",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_compositing_backend(backend: str) -> str:
            import json
            receipt = changeset.add("compositing_backend", {"backend": backend})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_compositing_backend() -> dict:
            return self.get()
