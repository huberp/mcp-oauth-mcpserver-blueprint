"""GitHub API client for making authenticated requests."""

from typing import Any

import httpx

from .config import settings


class GitHubAPIClient:
    """Client for making GitHub API requests with provided tokens."""

    def __init__(self) -> None:
        """Initialize GitHub API client."""
        self.base_url = settings.api_base_url
        self.timeout = settings.api_timeout

    async def get_user_info(self, token: str) -> dict[str, Any]:
        """
        Fetch user information from GitHub API using provided token.

        Args:
            token: GitHub access token

        Returns:
            User information dictionary

        Raises:
            ValueError: If token is invalid or API request fails
            httpx.HTTPError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MCP-OAuth-Server/1.0",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/user", headers=headers)
            if response.status_code == 401:
                raise ValueError("Invalid or expired GitHub token")
            response.raise_for_status()
            return response.json()

    async def get_user_repos(self, token: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Fetch user's repositories from GitHub API using provided token.

        Args:
            token: GitHub access token
            limit: Maximum number of repositories to return

        Returns:
            List of repository dictionaries

        Raises:
            ValueError: If token is invalid or API request fails
            httpx.HTTPError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MCP-OAuth-Server/1.0",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/user/repos",
                headers=headers,
                params={"per_page": limit, "sort": "updated"},
            )
            if response.status_code == 401:
                raise ValueError("Invalid or expired GitHub token")
            response.raise_for_status()
            return response.json()

    async def make_authenticated_request(
        self,
        token: str,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Make an authenticated API request.

        Args:
            token: GitHub access token
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Optional query parameters
            json: Optional JSON body

        Returns:
            Response JSON dictionary

        Raises:
            ValueError: If token is invalid or API request fails
            httpx.HTTPError: If API request fails
        """
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "MCP-OAuth-Server/1.0",
        }

        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(
                method=method, url=url, headers=headers, params=params, json=json
            )
            if response.status_code == 401:
                raise ValueError("Invalid or expired GitHub token")
            response.raise_for_status()
            return response.json()


# Legacy API client for backward compatibility
class APIClient:
    """Legacy API client - deprecated, use GitHubAPIClient instead."""

    def __init__(self, oauth_metadata) -> None:
        """Initialize legacy API client."""
        self.oauth_metadata = oauth_metadata
        self.base_url = settings.api_base_url
        self.timeout = settings.api_timeout

    async def get_user_info(self) -> dict[str, Any]:
        """Legacy method - not supported in new architecture."""
        raise NotImplementedError(
            "This method requires client-managed authentication. "
            "Use GitHubAPIClient.get_user_info(token) instead."
        )

    async def get_user_repos(self, limit: int = 10) -> list[dict[str, Any]]:
        """Legacy method - not supported in new architecture."""
        raise NotImplementedError(
            "This method requires client-managed authentication. "
            "Use GitHubAPIClient.get_user_repos(token, limit) instead."
        )

    async def make_authenticated_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Legacy method - not supported in new architecture."""
        raise NotImplementedError(
            "This method requires client-managed authentication. "
            "Use GitHubAPIClient.make_authenticated_request(token, ...) instead."
        )