import json
import logging
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.auth.providers.github import GitHubProvider

from mcp_server.api_client import APIClient
from mcp_server.config import settings

# Initialize logger
logger = logging.getLogger(__name__)

api_client = APIClient()

# The GitHubProvider handles GitHub's token format and validation
auth_provider = GitHubProvider(
    client_id=settings.oauth_client_id,  # Your GitHub OAuth App Client ID
    client_secret=settings.oauth_client_secret,     # Your GitHub OAuth App Client Secret
    base_url="http://localhost:8000",   # Must match your OAuth App configuration
    # redirect_path="/auth/callback"   # Default value, customize if needed
)

mcp = FastMCP(name=settings.server_name, auth=auth_provider)

# Add a protected tool to test authentication
@mcp.tool
async def get_user_info() -> dict:
    """Returns information about the authenticated GitHub user."""
    from fastmcp.server.dependencies import get_access_token

    token = get_access_token()
    # The GitHubProvider stores user data in token claims
    return {
        "github_user": token.claims.get("login"),
        "name": token.claims.get("name"),
        "email": token.claims.get("email")
    }

@mcp.tool()
async def get_github_user_info(
    include_repos: bool = True,
    repo_limit: int = 10
) -> str:
    """
    Fetch authenticated GitHub user information and repositories using OAuth.

    This tool requires OAuth authentication and retrieves the user's profile
    and recent repositories. Returns structured data about the user and their repositories.

    Args:
        include_repos: Whether to include repository information (default: True)
        repo_limit: Maximum number of repositories to fetch (1-100, default: 10)

    Returns:
        JSON string containing user profile and repository information

    Raises:
        ValueError: If OAuth is not configured or user is not authenticated
    """
    from fastmcp.server.dependencies import get_access_token
    token = get_access_token()

    # Check if authenticated
    if not token:
        error_msg = "OAuth authentication required. Please authenticate with GitHub first."
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
