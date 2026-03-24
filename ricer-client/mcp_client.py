"""
MCP Client
----------
Connects to the ricer-mcp server over stdio, discovers tools and
resources, and exposes simple helpers the orchestrator can call.
"""

from __future__ import annotations

import os
import json
import sys
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """Thin wrapper around an MCP ClientSession."""

    def __init__(self, server_script: str | None = None) -> None:
        self._server_script = server_script or os.getenv(
            "MCP_SERVER_PATH", "../ricer-mcp/server.py"
        )
        self._session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()
        self.tools: list[dict] = []           # raw tool descriptions
        self.resources: list[dict] = []       # raw resource descriptions

    # ── Lifecycle ────────────────────────────────────────────────────

    async def connect(self) -> None:
        """Start the MCP server as a subprocess and connect over stdio."""
        server_script_abs = os.path.abspath(self._server_script)
        server_cwd = os.path.dirname(server_script_abs)

        server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script_abs],
            env=os.environ.copy(),
            cwd=server_cwd,
        )

        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = stdio_transport

        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()

        # Cache tool + resource metadata
        await self._refresh_metadata()

        self.provider_name = "unknown"
        try:
            self.provider_name = await self.call_tool("get_provider_info", {})
        except Exception:
            pass

        print(
            f"[mcp] Connected — provider: {self.provider_name}, "
            f"{len(self.tools)} tools, {len(self.resources)} resources"
        )

    async def disconnect(self) -> None:
        """Tear down the server subprocess."""
        try:
            if self._session:
                try:
                    # Try to close the session gracefully
                    await self._session.close()
                except Exception:
                    pass
                self._session = None
            
            # Close the exit stack which manages all context managers
            await self._exit_stack.aclose()
        except RuntimeError as e:
            # Handle "Attempted to exit cancel scope in a different task" error
            # This can happen if the event loop is stopping while contexts are closing
            if "cancel scope" in str(e).lower():
                pass
            else:
                raise
        except Exception:
            # Ignore other errors during disconnect - we're shutting down anyway
            pass

    # ── Discovery ────────────────────────────────────────────────────

    async def _refresh_metadata(self) -> None:
        if not self._session:
            raise RuntimeError("Not connected")

        tools_response = await self._session.list_tools()
        self.tools = [
            {
                "name": t.name,
                "description": t.description or "",
                "input_schema": t.inputSchema,
            }
            for t in tools_response.tools
        ]

        resources_response = await self._session.list_resources()
        self.resources = [
            {
                "uri": str(r.uri),
                "name": r.name,
                "description": r.description or "",
            }
            for r in resources_response.resources
        ]

        print(f"[mcp] Available resources: {[r['uri'] for r in self.resources]}")

    def get_openai_tools(self) -> list[dict]:
        """
        Return tools formatted for the OpenAI function-calling API.
        This is what we send to the LLM so it knows which tools exist.
        """
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            }
            for tool in self.tools
        ]

        # Expose MCP resources through a single function-like tool so
        # the LLM can read current settings before proposing changes.
        if self.resources:
            resource_items = [
                f"- {r['uri']}: {r['description'] or r['name']}"
                for r in self.resources
            ]
            openai_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": "read_resource",
                        "description": (
                            "Read a current desktop setting from a resource URI.\n"
                            "Available resources:\n"
                            + "\n".join(resource_items)
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "uri": {
                                    "type": "string",
                                    "description": "Resource URI to read.",
                                    "enum": [r["uri"] for r in self.resources],
                                }
                            },
                            "required": ["uri"],
                            "additionalProperties": False,
                        },
                    },
                }
            )

        return openai_tools

    # ── Execution ────────────────────────────────────────────────────

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Call a tool on the MCP server and return the text result."""
        if not self._session:
            raise RuntimeError("Not connected")

        result = await self._session.call_tool(name, arguments)

        # MCP returns a list of content blocks; join their text.
        parts: list[str] = []
        for block in result.content:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts) if parts else "(no output)"

    async def read_resource(self, uri: str) -> str:
        """Read a resource from the MCP server and return its text."""
        if not self._session:
            raise RuntimeError("Not connected")

        result = await self._session.read_resource(uri)

        parts: list[str] = []
        for block in result.contents:
            if hasattr(block, "text"):
                parts.append(block.text)
        return "\n".join(parts) if parts else "(no output)"
