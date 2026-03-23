"""Feature: latency policy (input)."""

from feature import Feature, FeatureType
from utils.write.kwriteconfig import write_kde_config
from utils.read.kreadconfig import read_kde_config
from utils.reload.reconfigure_kwin import reconfigure_kwin

class LatencyPolicyFeature(Feature):
    type = FeatureType.INPUT

    def set(self, policy: str) -> bool:
        success = write_kde_config("kwinrc", "Compositing", "LatencyPolicy", policy)
        if success:
            reconfigure_kwin()
        return success

    def get(self) -> dict:
        value = read_kde_config("kwinrc", "Compositing", "LatencyPolicy", "PreferAccuracy")
        return {
            "setting": "latency_policy",
            "file": "kwinrc",
            "group": "Compositing",
            "key": "LatencyPolicy",
            "value": value,
        }

    def register_tool(self, mcp, changeset) -> None:
        @mcp.tool()
        def set_latency_policy(policy: str) -> str:
            import json
            receipt = changeset.add("latency_policy", {"policy": policy})
            return json.dumps(receipt)

    def register_resource(self, mcp) -> None:
        @mcp.resource()
        def get_latency_policy() -> dict:
            return self.get()
