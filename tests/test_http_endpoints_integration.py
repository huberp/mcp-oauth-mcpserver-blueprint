"""Integration tests for HTTP endpoints with running server."""

import pytest
from starlette.testclient import TestClient

from mcp_server.server import mcp


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the MCP server."""
    app = mcp.http_app()
    return TestClient(app)


def test_health_endpoint_integration(client: TestClient) -> None:
    """Test health endpoint via test client."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["server"] == "mcp-oauth-server"
    assert "uptime_seconds" in data


def test_metrics_endpoint_integration(client: TestClient) -> None:
    """Test metrics endpoint via test client."""
    response = client.get("/metrics")
    assert response.status_code == 200

    data = response.json()
    assert "tool_calls" in data
    assert "total" in data["tool_calls"]
    assert "by_tool" in data["tool_calls"]


def test_info_endpoint_integration(client: TestClient) -> None:
    """Test info endpoint via test client."""
    response = client.get("/info")
    assert response.status_code == 200

    data = response.json()
    assert "server" in data
    assert "github" in data
    assert "oauth" in data
    assert data["github"]["repository"] == "huberp/mcp-oauth-mcpserver-blueprint"


def test_all_endpoints_return_json(client: TestClient) -> None:
    """Test that all endpoints return valid JSON."""
    endpoints = ["/health", "/metrics", "/info"]

    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        # Verify it's valid JSON by parsing
        data = response.json()
        assert isinstance(data, dict)
