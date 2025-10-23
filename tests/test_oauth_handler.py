"""Tests for OAuth handler module."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import respx
from httpx import Response

from mcp_server.oauth_handler import OAuthHandler


@pytest.fixture
def oauth_handler() -> OAuthHandler:
    """Create an OAuth handler instance for testing."""
    return OAuthHandler()


def test_oauth_handler_initialization(oauth_handler: OAuthHandler) -> None:
    """Test OAuth handler initializes correctly."""
    assert oauth_handler.client_id == "test_client_id"
    assert oauth_handler.client_secret == "test_client_secret"
    assert oauth_handler.access_token is None
    assert oauth_handler.refresh_token is None


def test_generate_pkce_pair(oauth_handler: OAuthHandler) -> None:
    """Test PKCE code verifier and challenge generation."""
    code_verifier, code_challenge = oauth_handler.generate_pkce_pair()

    assert isinstance(code_verifier, str)
    assert isinstance(code_challenge, str)
    assert len(code_verifier) > 0
    assert len(code_challenge) > 0
    assert code_verifier != code_challenge


def test_get_authorization_url(oauth_handler: OAuthHandler) -> None:
    """Test authorization URL generation."""
    url, state, code_verifier = oauth_handler.get_authorization_url()

    assert "test.example.com/oauth/authorize" in url
    assert "client_id=test_client_id" in url
    assert "response_type=code" in url
    assert f"state={state}" in url
    assert "code_challenge=" in url
    assert "code_challenge_method=S256" in url
    assert isinstance(state, str)
    assert isinstance(code_verifier, str)


def test_get_authorization_url_with_state(oauth_handler: OAuthHandler) -> None:
    """Test authorization URL with custom state."""
    custom_state = "my_custom_state_123"
    url, state, code_verifier = oauth_handler.get_authorization_url(state=custom_state)

    assert f"state={custom_state}" in url
    assert state == custom_state


@pytest.mark.asyncio
@respx.mock
async def test_exchange_code_for_token(
    oauth_handler: OAuthHandler, mock_token_response: dict[str, Any]
) -> None:
    """Test exchanging authorization code for token."""
    # Mock the token endpoint
    respx.post("https://test.example.com/oauth/token").mock(
        return_value=Response(200, json=mock_token_response)
    )

    code_verifier = "test_code_verifier_123"
    token = await oauth_handler.exchange_code_for_token(
        code="test_auth_code", code_verifier=code_verifier
    )

    assert token["access_token"] == "test_access_token_12345"
    assert token["refresh_token"] == "test_refresh_token_67890"
    assert oauth_handler.access_token == "test_access_token_12345"
    assert oauth_handler.refresh_token == "test_refresh_token_67890"


@pytest.mark.asyncio
@respx.mock
async def test_refresh_access_token(
    oauth_handler: OAuthHandler, mock_token_response: dict[str, Any]
) -> None:
    """Test refreshing access token."""
    # Set initial refresh token
    oauth_handler.refresh_token = "test_refresh_token_67890"

    # Mock the token endpoint
    new_token_response = {
        "access_token": "new_access_token_12345",
        "token_type": "bearer",
        "scope": "read:user repo",
    }
    respx.post("https://test.example.com/oauth/token").mock(
        return_value=Response(200, json=new_token_response)
    )

    token = await oauth_handler.refresh_access_token()

    assert token["access_token"] == "new_access_token_12345"
    assert oauth_handler.access_token == "new_access_token_12345"


@pytest.mark.asyncio
async def test_refresh_access_token_no_refresh_token(oauth_handler: OAuthHandler) -> None:
    """Test refresh token fails without refresh token."""
    with pytest.raises(ValueError, match="No refresh token available"):
        await oauth_handler.refresh_access_token()


def test_get_auth_headers(oauth_handler: OAuthHandler) -> None:
    """Test getting authorization headers."""
    oauth_handler.access_token = "test_token_123"
    headers = oauth_handler.get_auth_headers()

    assert "Authorization" in headers
    assert headers["Authorization"] == "Bearer test_token_123"


def test_get_auth_headers_no_token(oauth_handler: OAuthHandler) -> None:
    """Test getting auth headers fails without token."""
    with pytest.raises(ValueError, match="No access token available"):
        oauth_handler.get_auth_headers()


def test_is_authenticated_true(oauth_handler: OAuthHandler) -> None:
    """Test authentication check returns True when authenticated."""
    oauth_handler.access_token = "test_token_123"
    assert oauth_handler.is_authenticated() is True


def test_is_authenticated_false(oauth_handler: OAuthHandler) -> None:
    """Test authentication check returns False when not authenticated."""
    assert oauth_handler.is_authenticated() is False
