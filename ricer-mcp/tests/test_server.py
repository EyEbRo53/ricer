"""Tests for MCP server setup and provider info."""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.mark.asyncio
async def test_server_initialization():
    """Test that the MCP server can be imported without errors."""
    try:
        # This test verifies the server module can be loaded
        # Actual server execution requires subprocess/stdio setup
        import server
        assert hasattr(server, 'mcp')
    except ImportError as e:
        pytest.skip(f"Server module dependencies not available: {e}")


@pytest.mark.asyncio
async def test_get_provider_info_tool_exists():
    """Test that get_provider_info tool is defined."""
    try:
        from server import mcp
        
        # Check if tools are registered
        tools = await mcp.list_tools()
        assert len(tools) > 0, "No tools registered"
        
        # Check for get_provider_info tool
        tool_names = [tool.name for tool in tools]
        assert "get_provider_info" in tool_names, f"get_provider_info not found in {tool_names}"
    except ImportError:
        pytest.skip("Server module not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])