"""Tests for HTTP endpoints (health, metrics, info)."""

import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_server.http_endpoints import (
    get_tool_call_counts,
    health_endpoint,
    increment_tool_call,
    info_endpoint,
    metrics_endpoint,
)


@pytest.fixture
def mock_request() -> Request:
    """Create a mock Starlette request."""
    mock = MagicMock(spec=Request)
    return mock


@pytest.fixture(autouse=True)
def reset_metrics() -> None:
    """Reset tool call metrics before each test."""
    # Import the private variable to reset it
    from mcp_server import http_endpoints

    http_endpoints._tool_call_counts.clear()


def test_increment_tool_call() -> None:
    """Test that tool call counts are incremented correctly."""
    # Initially empty
    assert get_tool_call_counts() == {}

    # Increment a tool
    increment_tool_call("test_tool")
    assert get_tool_call_counts() == {"test_tool": 1}

    # Increment again
    increment_tool_call("test_tool")
    assert get_tool_call_counts() == {"test_tool": 2}

    # Increment different tool
    increment_tool_call("another_tool")
    counts = get_tool_call_counts()
    assert counts == {"test_tool": 2, "another_tool": 1}


def test_get_tool_call_counts_returns_copy() -> None:
    """Test that get_tool_call_counts returns a copy, not the original dict."""
    increment_tool_call("test_tool")
    counts1 = get_tool_call_counts()
    counts2 = get_tool_call_counts()

    # Modifying the returned dict should not affect the original
    counts1["fake_tool"] = 999
    assert get_tool_call_counts() == {"test_tool": 1}
    assert counts2 == {"test_tool": 1}


@pytest.mark.asyncio
async def test_health_endpoint(mock_request: Request) -> None:
    """Test health endpoint returns correct status."""
    response = await health_endpoint(mock_request)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200

    # Parse response body
    body = json.loads(response.body.decode())

    assert body["status"] == "healthy"
    assert body["server"] == "mcp-oauth-server"
    assert body["version"] == "0.1.0"
    assert "uptime_seconds" in body
    assert "timestamp" in body
    assert isinstance(body["uptime_seconds"], (int, float))
    assert body["uptime_seconds"] >= 0


@pytest.mark.asyncio
async def test_health_endpoint_timestamp_format(mock_request: Request) -> None:
    """Test health endpoint timestamp is in ISO format."""
    response = await health_endpoint(mock_request)
    body = json.loads(response.body.decode())

    # Verify timestamp is valid ISO format with Z suffix
    timestamp = body["timestamp"]
    assert timestamp.endswith("Z")
    # Should be parseable
    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


@pytest.mark.asyncio
async def test_metrics_endpoint_no_calls(mock_request: Request) -> None:
    """Test metrics endpoint with no tool calls."""
    response = await metrics_endpoint(mock_request)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200

    body = json.loads(response.body.decode())

    assert body["server"] == "mcp-oauth-server"
    assert body["version"] == "0.1.0"
    assert "uptime_seconds" in body
    assert "timestamp" in body
    assert body["tool_calls"]["total"] == 0
    assert body["tool_calls"]["by_tool"] == {}


@pytest.mark.asyncio
async def test_metrics_endpoint_with_calls(mock_request: Request) -> None:
    """Test metrics endpoint with tool calls."""
    # Simulate some tool calls
    increment_tool_call("get_user_info")
    increment_tool_call("get_user_info")
    increment_tool_call("get_github_user_info")

    response = await metrics_endpoint(mock_request)
    body = json.loads(response.body.decode())

    assert body["tool_calls"]["total"] == 3
    assert body["tool_calls"]["by_tool"] == {
        "get_user_info": 2,
        "get_github_user_info": 1,
    }


@pytest.mark.asyncio
async def test_info_endpoint(mock_request: Request) -> None:
    """Test info endpoint returns server information."""
    response = await info_endpoint(mock_request)

    assert isinstance(response, JSONResponse)
    assert response.status_code == 200

    body = json.loads(response.body.decode())

    # Check server info
    assert body["server"]["name"] == "mcp-oauth-server"
    assert body["server"]["version"] == "0.1.0"
    assert body["server"]["environment"] == "test"
    assert isinstance(body["server"]["debug"], bool)

    # Check GitHub info
    assert body["github"]["repository"] == "huberp/mcp-oauth-mcpserver-blueprint"
    assert body["github"]["url"] == "https://github.com/huberp/mcp-oauth-mcpserver-blueprint"

    # Check OAuth info
    assert isinstance(body["oauth"]["configured"], bool)
    assert body["oauth"]["provider"] == "GitHub"
    assert isinstance(body["oauth"]["scopes"], list)

    # Check HTTP info
    assert "host" in body["http"]
    assert "port" in body["http"]
    assert "path" in body["http"]

    # Check API info
    assert "base_url" in body["api"]
    assert "timeout" in body["api"]

    # Check timestamp
    assert "timestamp" in body


@pytest.mark.asyncio
async def test_info_endpoint_oauth_configured(mock_request: Request) -> None:
    """Test info endpoint shows OAuth as configured when credentials are present."""
    response = await info_endpoint(mock_request)
    body = json.loads(response.body.decode())

    # OAuth should be configured in test environment (set in conftest.py)
    assert body["oauth"]["configured"] is True
    assert body["oauth"]["scopes"] == ["read:user"]


@pytest.mark.asyncio
async def test_info_endpoint_timestamp_format(mock_request: Request) -> None:
    """Test info endpoint timestamp is in ISO format."""
    response = await info_endpoint(mock_request)
    body = json.loads(response.body.decode())

    # Verify timestamp is valid ISO format with Z suffix
    timestamp = body["timestamp"]
    assert timestamp.endswith("Z")
    # Should be parseable
    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
