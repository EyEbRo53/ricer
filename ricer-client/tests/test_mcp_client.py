"""Tests for MCPClient connection and resource discovery."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_client import MCPClient


@pytest.mark.asyncio
async def test_mcp_client_init():
    """Test MCPClient initialization."""
    client = MCPClient()
    assert client.tools == []
    assert client.resources == []
    assert client._session is None


@pytest.mark.asyncio
async def test_mcp_client_custom_server_path():
    """Test MCPClient with custom server path."""
    custom_path = "/custom/path/server.py"
    client = MCPClient(server_script=custom_path)
    assert client._server_script == custom_path


@pytest.mark.asyncio
async def test_mcp_client_default_server_path(monkeypatch):
    """Test MCPClient uses environment variable for server path."""
    test_path = "/test/server.py"
    monkeypatch.setenv("MCP_SERVER_PATH", test_path)
    client = MCPClient(server_script=None)
    assert client._server_script == test_path


@pytest.mark.asyncio
async def test_get_openai_tools_empty():
    """Test get_openai_tools returns empty list when no tools are available."""
    client = MCPClient()
    client.tools = []
    client.resources = []
    tools = client.get_openai_tools()
    assert isinstance(tools, list)
    # Should return empty or [read_resource] if resources exist
    assert all(tool.get("type") == "function" for tool in tools)


@pytest.mark.asyncio
async def test_get_openai_tools_with_tools():
    """Test get_openai_tools formats tools correctly for OpenAI."""
    client = MCPClient()
    
    # Mock some tools
    client.tools = [
        {
            "name": "test_tool",
            "description": "A test tool",
            "input_schema": {
                "type": "object",
                "properties": {"arg": {"type": "string"}},
            },
        }
    ]
    client.resources = []
    
    tools = client.get_openai_tools()
    assert len(tools) == 1
    assert tools[0]["type"] == "function"
    assert tools[0]["function"]["name"] == "test_tool"
    assert tools[0]["function"]["description"] == "A test tool"


@pytest.mark.asyncio
async def test_get_openai_tools_with_resources():
    """Test get_openai_tools exposes resources as read_resource function."""
    client = MCPClient()
    client.tools = []
    client.resources = [
        {
            "uri": "kde://color-scheme",
            "name": "Color Scheme",
            "description": "Current KDE color scheme",
        },
        {
            "uri": "kde://theme",
            "name": "Theme",
            "description": "Current KDE theme",
        },
    ]
    
    tools = client.get_openai_tools()
    
    # Should have read_resource function
    resource_tools = [t for t in tools if t["function"]["name"] == "read_resource"]
    assert len(resource_tools) == 1
    
    resource_tool = resource_tools[0]
    assert resource_tool["type"] == "function"
    assert "color-scheme" in resource_tool["function"]["description"]
    assert "theme" in resource_tool["function"]["description"]
    
    # Check that enum contains all resource URIs
    uri_enum = resource_tool["function"]["parameters"]["properties"]["uri"]["enum"]
    assert "kde://color-scheme" in uri_enum
    assert "kde://theme" in uri_enum


@pytest.mark.asyncio
async def test_call_tool_not_connected():
    """Test call_tool raises RuntimeError when not connected."""
    client = MCPClient()
    
    with pytest.raises(RuntimeError, match="Not connected"):
        await client.call_tool("some_tool", {})


@pytest.mark.asyncio
async def test_read_resource_not_connected():
    """Test read_resource raises RuntimeError when not connected."""
    client = MCPClient()
    
    with pytest.raises(RuntimeError, match="Not connected"):
        await client.read_resource("kde://color-scheme")


@pytest.mark.asyncio
async def test_disconnect_when_not_connected():
    """Test disconnect when never connected doesn't raise error."""
    client = MCPClient()
    
    # Should not raise any exception
    try:
        await client.disconnect()
    except Exception as e:
        pytest.fail(f"disconnect() raised {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])