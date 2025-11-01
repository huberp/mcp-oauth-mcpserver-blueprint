"""API client for making OAuth-protected HTTP requests."""

from typing import Any

import httpx

from mcp_server.config import settings
from fastmcp.server.dependencies import get_access_token
from fastmcp.server.auth import AccessToken


class APIClient:
    """Client for making authenticated API requests."""

    def __init__(self) -> None:
        """
        Initialize API client with OAuth handler.
        """
        self.base_url = settings.api_base_url
        self.timeout = settings.api_timeout

    async def get_user_info(self, token: AccessToken) -> dict[str, Any]:
        """
        Fetch authenticated user information from GitHub API.

        Args:
            token: Access token for authentication

        Returns:
            User information dictionary

        Raises:
            httpx.HTTPError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/user", headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_user_repos(self, token: AccessToken, limit: int = 10) -> list[dict[str, Any]]:
        """
        Fetch authenticated user's repositories from GitHub API.

        Args:
            token: Access token for authentication
            limit: Maximum number of repositories to return

        Returns:
            List of repository dictionaries

        Raises:
            httpx.HTTPError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/user/repos",
                headers=headers,
                params={"per_page": limit, "sort": "updated"},
            )
            response.raise_for_status()
            return response.json()

    async def make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make an authenticated API request.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Optional query parameters
            json: Optional JSON body

        Returns:
            Response JSON dictionary

        Raises:
            ValueError: If not authenticated
            httpx.HTTPError: If API request fails
        """
        if not self.oauth_handler.is_authenticated():
            raise ValueError("Not authenticated. Please authenticate first.")

        headers = self.oauth_handler.get_auth_headers()
        headers["Accept"] = "application/vnd.github+json"
        headers["X-GitHub-Api-Version"] = "2022-11-28"

        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method, url=url, headers=headers, params=params, json=json
            )
            response.raise_for_status()
            return response.json()
