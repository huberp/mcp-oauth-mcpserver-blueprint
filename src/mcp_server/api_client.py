"""API client for OAuth-protected HTTP requests."""

import base64
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

    def _get_auth_headers(self, token: AccessToken) -> dict[str, str]:
        """Get common authentication headers."""
        return {
            "Authorization": f"Bearer {token.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

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
        headers = self._get_auth_headers(token)

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
        headers = self._get_auth_headers(token)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/user/repos",
                headers=headers,
                params={"per_page": limit, "sort": "updated"},
            )
            response.raise_for_status()
            return response.json()

    async def get_repository(self, token: AccessToken, owner: str, repo: str) -> dict[str, Any]:
        """
        Fetch repository metadata.

        Args:
            token: Access token for authentication
            owner: Repository owner/organization
            repo: Repository name

        Returns:
            Repository metadata dictionary

        Raises:
            httpx.HTTPError: If API request fails
        """
        headers = self._get_auth_headers(token)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/repos/{owner}/{repo}", headers=headers)
            response.raise_for_status()
            return response.json()

    async def get_readme(self, token: AccessToken, owner: str, repo: str) -> str:
        """
        Fetch repository README content.

        Args:
            token: Access token for authentication
            owner: Repository owner/organization
            repo: Repository name

        Returns:
            README content as string, empty if not found

        Raises:
            httpx.HTTPError: If API request fails (except 404)
        """
        headers = self._get_auth_headers(token)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(f"{self.base_url}/repos/{owner}/{repo}/readme", headers=headers)
                response.raise_for_status()
                content = response.json().get("content", "")
                return base64.b64decode(content).decode("utf-8")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    return ""  # No README found
                raise

    async def get_repository_languages(self, token: AccessToken, owner: str, repo: str) -> dict[str, int]:
        """
        Fetch repository language statistics.

        Args:
            token: Access token for authentication
            owner: Repository owner/organization
            repo: Repository name

        Returns:
            Dictionary mapping language names to byte counts

        Raises:
            httpx.HTTPError: If API request fails
        """
        headers = self._get_auth_headers(token)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(f"{self.base_url}/repos/{owner}/{repo}/languages", headers=headers)
            response.raise_for_status()
            return response.json()
