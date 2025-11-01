"""Tests for API client module."""

from typing import Any
from unittest.mock import MagicMock

import pytest
import respx
from fastmcp.server.auth import AccessToken
from httpx import Response

from mcp_server.api_client import APIClient


@pytest.fixture
def mock_token() -> AccessToken:
    """Create a mock access token."""
    token = MagicMock(spec=AccessToken)
    token.token = "test_access_token_12345"
    token.claims = {"login": "testuser", "name": "Test User"}
    return token


@pytest.fixture
def api_client() -> APIClient:
    """Create an API client instance."""
    return APIClient()


def test_api_client_initialization(api_client: APIClient) -> None:
    """Test API client initializes correctly."""
    assert api_client.base_url == "https://api.test.example.com"
    assert api_client.timeout == 30


@pytest.mark.asyncio
@respx.mock
async def test_get_user_info(
    api_client: APIClient, mock_token: AccessToken, mock_user_data: dict[str, Any]
) -> None:
    """Test fetching user information."""
    respx.get("https://api.test.example.com/user").mock(
        return_value=Response(200, json=mock_user_data)
    )

    user_info = await api_client.get_user_info(mock_token)

    assert user_info["login"] == "testuser"
    assert user_info["name"] == "Test User"
    assert user_info["public_repos"] == 42


@pytest.mark.asyncio
@respx.mock
async def test_get_user_repos(
    api_client: APIClient, mock_token: AccessToken, mock_repo_data: list[dict[str, Any]]
) -> None:
    """Test fetching user repositories."""
    respx.get("https://api.test.example.com/user/repos").mock(
        return_value=Response(200, json=mock_repo_data)
    )

    repos = await api_client.get_user_repos(mock_token, limit=10)

    assert len(repos) == 2
    assert repos[0]["name"] == "test-repo-1"
    assert repos[1]["name"] == "test-repo-2"


@pytest.mark.asyncio
@respx.mock
async def test_get_user_repos_custom_limit(api_client: APIClient, mock_token: AccessToken) -> None:
    """Test fetching repos with custom limit."""
    mock_data = [{"name": f"repo-{i}"} for i in range(5)]
    respx.get("https://api.test.example.com/user/repos").mock(
        return_value=Response(200, json=mock_data)
    )

    repos = await api_client.get_user_repos(mock_token, limit=5)

    assert len(repos) == 5
