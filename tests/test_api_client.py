"""Tests for API client module."""

from typing import Any
from unittest.mock import MagicMock

import pytest
import respx
from httpx import Response

from mcp_server.api_client import APIClient
from mcp_server.oauth_handler import OAuthHandler


@pytest.fixture
def oauth_handler() -> OAuthHandler:
    """Create an authenticated OAuth handler."""
    handler = OAuthHandler()
    handler.access_token = "test_access_token_12345"
    return handler


@pytest.fixture
def api_client(oauth_handler: OAuthHandler) -> APIClient:
    """Create an API client instance."""
    return APIClient(oauth_handler)


def test_api_client_initialization(oauth_handler: OAuthHandler) -> None:
    """Test API client initializes correctly."""
    client = APIClient(oauth_handler)
    assert client.oauth_handler == oauth_handler
    assert client.base_url == "https://api.test.example.com"


@pytest.mark.asyncio
@respx.mock
async def test_get_user_info(api_client: APIClient, mock_user_data: dict[str, Any]) -> None:
    """Test fetching user information."""
    respx.get("https://api.test.example.com/user").mock(
        return_value=Response(200, json=mock_user_data)
    )

    user_info = await api_client.get_user_info()

    assert user_info["login"] == "testuser"
    assert user_info["name"] == "Test User"
    assert user_info["public_repos"] == 42


@pytest.mark.asyncio
async def test_get_user_info_not_authenticated() -> None:
    """Test getting user info fails when not authenticated."""
    handler = OAuthHandler()
    client = APIClient(handler)

    with pytest.raises(ValueError, match="Not authenticated"):
        await client.get_user_info()


@pytest.mark.asyncio
@respx.mock
async def test_get_user_repos(api_client: APIClient, mock_repo_data: list[dict[str, Any]]) -> None:
    """Test fetching user repositories."""
    respx.get("https://api.test.example.com/user/repos").mock(
        return_value=Response(200, json=mock_repo_data)
    )

    repos = await api_client.get_user_repos(limit=10)

    assert len(repos) == 2
    assert repos[0]["name"] == "test-repo-1"
    assert repos[1]["name"] == "test-repo-2"


@pytest.mark.asyncio
async def test_get_user_repos_not_authenticated() -> None:
    """Test getting repos fails when not authenticated."""
    handler = OAuthHandler()
    client = APIClient(handler)

    with pytest.raises(ValueError, match="Not authenticated"):
        await client.get_user_repos()


@pytest.mark.asyncio
@respx.mock
async def test_make_authenticated_request(api_client: APIClient) -> None:
    """Test making an authenticated API request."""
    mock_response = {"message": "success"}
    respx.get("https://api.test.example.com/test/endpoint").mock(
        return_value=Response(200, json=mock_response)
    )

    response = await api_client.make_authenticated_request("GET", "/test/endpoint")

    assert response["message"] == "success"


@pytest.mark.asyncio
@respx.mock
async def test_make_authenticated_request_with_params(api_client: APIClient) -> None:
    """Test making an authenticated request with query parameters."""
    mock_response = {"results": []}
    respx.get("https://api.test.example.com/search").mock(
        return_value=Response(200, json=mock_response)
    )

    response = await api_client.make_authenticated_request(
        "GET", "/search", params={"q": "test", "limit": 10}
    )

    assert "results" in response


@pytest.mark.asyncio
async def test_make_authenticated_request_not_authenticated() -> None:
    """Test making authenticated request fails when not authenticated."""
    handler = OAuthHandler()
    client = APIClient(handler)

    with pytest.raises(ValueError, match="Not authenticated"):
        await client.make_authenticated_request("GET", "/test")
