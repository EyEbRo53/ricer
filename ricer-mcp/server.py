from mcp.server.fastmcp import FastMCP
from changeset import changeset
from tools import register_all
from resources import register_all as register_all_resources

mcp = FastMCP("ricer-mcp")

# Register all staging tools (input + display) on the MCP server.
# Each tool adds an entry to the shared changeset — nothing executes
# until confirm_change() is called.
register_all(mcp, changeset)

# Register all read-only resources (input + display) on the MCP server.
# Each resource reads the current Plasma config via kreadconfig6 / DBus.
register_all_resources(mcp)


if __name__ == "__main__":
    mcp.run()
