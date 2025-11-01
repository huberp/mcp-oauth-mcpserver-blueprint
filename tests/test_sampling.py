"""Tests for MCP sampling capability."""

import pytest
from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider

from mcp_server.server import mcp


@pytest.mark.asyncio
async def test_server_is_fastmcp_instance() -> None:
    """Test that server is a FastMCP instance."""
    assert isinstance(mcp, FastMCP)


@pytest.mark.asyncio
async def test_server_has_auth_provider() -> None:
    """Test that server has auth provider configured."""
    # Verify the server has auth configured
    assert mcp.auth is not None
    # Verify it's a GitHubProvider
    assert isinstance(mcp.auth, GitHubProvider)
