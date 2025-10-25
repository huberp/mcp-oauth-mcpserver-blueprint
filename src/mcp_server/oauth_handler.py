"""OAuth 2.1 authentication handler with PKCE and RFC 8707 Resource Indicators support.

This module implements OAuth 2.1 flows as an OAuth Resource Server per MCP Specification 2025-06-18.
It supports RFC 8707 Resource Indicators for enhanced security.
"""

import secrets
from typing import Any
from urllib.parse import urlencode

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc7636 import create_s256_code_challenge

from .config import settings


class OAuthHandler:
    """
    Handles OAuth 2.1 authentication flows with PKCE and Resource Indicators support.

    This class implements OAuth Resource Server behavior as per MCP Specification 2025-06-18,
    including support for RFC 8707 Resource Indicators for token scoping.
    """

    def __init__(self, resource_uri: str | None = None) -> None:
        """
        Initialize OAuth handler with configuration.

        Args:
            resource_uri: Optional resource URI for RFC 8707 Resource Indicators.
                         If not provided, uses the API base URL from settings.
        """
        self.client_id = settings.oauth_client_id
        self.client_secret = settings.oauth_client_secret
        self.authorization_url = settings.oauth_authorization_url
        self.token_url = settings.oauth_token_url
        self.scopes = settings.oauth_scopes_list
        self.resource_uri = resource_uri or settings.api_base_url
        self.access_token: str | None = None
        self.refresh_token: str | None = None
        self._code_verifier: str | None = None

    def generate_pkce_pair(self) -> tuple[str, str]:
        """
        Generate PKCE code verifier and challenge.

        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        code_verifier = secrets.token_urlsafe(64)
        code_challenge = create_s256_code_challenge(code_verifier)
        return code_verifier, code_challenge

    def get_authorization_url(self, state: str | None = None) -> tuple[str, str, str]:
        """
        Generate OAuth authorization URL with PKCE.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Tuple of (authorization_url, state, code_verifier)
        """
        if state is None:
            state = secrets.token_urlsafe(32)

        code_verifier, code_challenge = self.generate_pkce_pair()
        self._code_verifier = code_verifier

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost:8080/callback",
            "scope": " ".join(self.scopes),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        url = f"{self.authorization_url}?{urlencode(params)}"
        return url, state, code_verifier

    async def exchange_code_for_token(
        self, code: str, code_verifier: str, redirect_uri: str = "http://localhost:8080/callback"
    ) -> dict[str, Any]:
        """
        Exchange authorization code for access token with Resource Indicator (RFC 8707).

        Args:
            code: Authorization code from OAuth provider
            code_verifier: PKCE code verifier
            redirect_uri: Redirect URI used in authorization

        Returns:
            Token response dictionary

        Raises:
            httpx.HTTPError: If token exchange fails
        """
        async with AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_endpoint=self.token_url,
        ) as client:
            # Include RFC 8707 Resource Indicator for token scoping
            token = await client.fetch_token(
                url=self.token_url,
                grant_type="authorization_code",
                code=code,
                code_verifier=code_verifier,
                redirect_uri=redirect_uri,
                resource=self.resource_uri,  # RFC 8707 Resource Indicator
            )

            self.access_token = token.get("access_token")
            self.refresh_token = token.get("refresh_token")

            return token

    async def refresh_access_token(self) -> dict[str, Any]:
        """
        Refresh access token using refresh token with Resource Indicator (RFC 8707).

        Returns:
            New token response dictionary

        Raises:
            ValueError: If no refresh token is available
            httpx.HTTPError: If token refresh fails
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")

        async with AsyncOAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_endpoint=self.token_url,
        ) as client:
            # Include RFC 8707 Resource Indicator for token scoping
            token = await client.refresh_token(
                url=self.token_url,
                refresh_token=self.refresh_token,
                resource=self.resource_uri,  # RFC 8707 Resource Indicator
            )

            self.access_token = token.get("access_token")
            self.refresh_token = token.get("refresh_token", self.refresh_token)

            return token

    def get_auth_headers(self) -> dict[str, str]:
        """
        Get authorization headers for API requests.

        Returns:
            Dictionary with Authorization header

        Raises:
            ValueError: If no access token is available
        """
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")

        return {"Authorization": f"Bearer {self.access_token}"}

    def is_authenticated(self) -> bool:
        """Check if user is authenticated with valid token."""
        return self.access_token is not None

    def get_resource_uri(self) -> str:
        """
        Get the resource URI for RFC 8707 Resource Indicators.

        Returns:
            The resource URI that tokens are scoped to
        """
        return self.resource_uri

    def get_authorization_error_response(self) -> dict[str, Any]:
        """
        Generate standardized authorization error response for MCP clients.

        Returns a structured error response that clients can use to automatically
        discover and initiate OAuth flows. This follows MCP spec guidance for
        stdio transport where WWW-Authenticate headers aren't available.

        Returns:
            Dictionary containing error code, message, and OAuth metadata
        """
        return {
            "code": -32001,  # Custom error code for authentication required
            "message": "Authentication required",
            "data": {
                "type": "oauth2",
                "grant_type": "authorization_code",
                "authorization_url": self.authorization_url,
                "token_url": self.token_url,
                "scopes": self.scopes,
                "code_challenge_method": "S256",
                "resource": self.resource_uri,
            },
        }
