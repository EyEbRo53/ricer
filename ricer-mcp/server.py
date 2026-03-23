from mcp.server.fastmcp import FastMCP
from changeset import changeset
from provider_runtime import ensure_provider_paths

ensure_provider_paths()

from features import register_all
from resources import register_all as register_all_resources

mcp = FastMCP("ricer-mcp")

# Register all feature modules (each provides both tool + resource)
# on the MCP server. Tools add entries to the shared changeset;
# nothing executes until confirm_change() is called.
register_all(mcp, changeset)
register_all_resources(mcp)


if __name__ == "__main__":
    mcp.run()
