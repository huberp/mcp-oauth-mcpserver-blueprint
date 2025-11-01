"""MCP server implementation with FastMCP OAuth handling."""

import json
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider
from fastmcp.server.dependencies import get_access_token

from mcp_server.api_client import APIClient
from mcp_server.config import settings
from mcp_server.http_endpoints import (
    health_endpoint,
    increment_tool_call,
    info_endpoint,
    metrics_endpoint,
)

logger = logging.getLogger(__name__)

api_client = APIClient()

# GitHubProvider handles GitHub token format and validation
auth_provider = GitHubProvider(
    client_id=settings.oauth_client_id,
    client_secret=settings.oauth_client_secret,
    base_url="http://localhost:8000",  # Must match OAuth App configuration
    # redirect_path="/auth/callback"   # Default, customize if needed
)

mcp = FastMCP(name=settings.server_name, auth=auth_provider)


# Register custom HTTP endpoints
@mcp.custom_route("/health", methods=["GET"])
async def health_route(request: Any) -> Any:
    """Health check endpoint."""
    return await health_endpoint(request)


@mcp.custom_route("/metrics", methods=["GET"])
async def metrics_route(request: Any) -> Any:
    """Metrics endpoint with tool call statistics."""
    return await metrics_endpoint(request)


@mcp.custom_route("/info", methods=["GET"])
async def info_route(request: Any) -> Any:
    """Server information endpoint."""
    return await info_endpoint(request)


# Decorator to track tool calls
def track_tool_call(tool_name: str) -> Callable:
    """
    Decorator to track tool calls for metrics.

    Args:
        tool_name: Name of the tool being called

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            increment_tool_call(tool_name)
            return await func(*args, **kwargs)

        return wrapper

    return decorator


@mcp.tool
@track_tool_call("get_user_info")
async def get_user_info() -> dict:
    """Return authenticated GitHub user information."""
    token = get_access_token()
    # GitHubProvider stores user data in token claims
    return {
        "github_user": token.claims.get("login"),
        "name": token.claims.get("name"),
        "email": token.claims.get("email"),
    }


@mcp.tool()
@track_tool_call("get_github_user_info")
async def get_github_user_info(include_repos: bool = True, repo_limit: int = 10) -> str:
    """
    Fetch authenticated user info and repos from GitHub.

    Requires OAuth authentication. Returns user profile and repository data.

    Args:
        include_repos: Include repository information (default: True)
        repo_limit: Max repositories to fetch, 1-100 (default: 10)

    Returns:
        JSON string with user profile and repository data

    Raises:
        ValueError: If not authenticated or API call fails
    """
    token = get_access_token()

    # Verify authentication
    if not token:
        error_msg = "OAuth authentication required. Authenticate with GitHub first."
        logger.warning("User not authenticated")
        raise ValueError(error_msg)

    try:
        # Fetch user info
        user_info = await api_client.get_user_info(token)

        result: dict[str, Any] = {
            "login": user_info.get("login"),
            "name": user_info.get("name"),
            "bio": user_info.get("bio"),
            "public_repos": user_info.get("public_repos"),
            "followers": user_info.get("followers"),
            "following": user_info.get("following"),
            "created_at": user_info.get("created_at"),
            "updated_at": user_info.get("updated_at"),
        }

        # Optionally fetch repositories
        if include_repos:
            repos = await api_client.get_user_repos(token, limit=repo_limit)

            result["repositories"] = [
                {
                    "name": repo.get("name"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "stars": repo.get("stargazers_count"),
                    "forks": repo.get("forks_count"),
                    "updated_at": repo.get("updated_at"),
                    "url": repo.get("html_url"),
                }
                for repo in repos
            ]

        result_text = json.dumps(result, indent=2)
        logger.info("Successfully fetched GitHub user info")
        return result_text

    except Exception as e:
        error_msg = f"Error fetching GitHub user info: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise ValueError(error_msg) from e
