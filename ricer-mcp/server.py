from mcp.server.fastmcp import FastMCP
from changeset import changeset
from features import register_all

mcp = FastMCP("ricer-mcp")

# Register all feature modules (each provides both tool + resource)
# on the MCP server. Tools add entries to the shared changeset;
# nothing executes until confirm_change() is called.
register_all(mcp, changeset)


if __name__ == "__main__":
    mcp.run()
