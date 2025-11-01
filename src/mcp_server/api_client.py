"""API client for OAuth-protected HTTP requests."""

from typing import Any

import httpx
from fastmcp.server.auth import AccessToken

from mcp_server.config import settings


class APIClient:
    """Client for authenticated API requests."""

    def __init__(self) -> None:
        """Initialize API client."""
        self.base_url = settings.api_base_url
        self.timeout = settings.api_timeout

    async def get_user_info(self, token: AccessToken) -> dict[str, Any]:
        """
        Fetch authenticated user info from GitHub API.

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
            "X-GitHub-Api-Version": "2022-11-28",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/user", headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_user_repos(
        self, token: AccessToken, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Fetch authenticated user's repos from GitHub API.

        Args:
            token: Access token for authentication
            limit: Max repositories to return

        Returns:
            List of repository dictionaries

        Raises:
            httpx.HTTPError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/user/repos",
                headers=headers,
                params={"per_page": limit, "sort": "updated"},
            )
            response.raise_for_status()
            return response.json()
