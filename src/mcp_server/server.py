"""MCP server implementation with FastMCP OAuth handling."""

import json
import logging
from typing import Any

from fastmcp import FastMCP, Context
from fastmcp.server.auth.providers.github import GitHubProvider
from fastmcp.server.dependencies import get_access_token

from mcp_server.api_client import APIClient
from mcp_server.config import settings

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


@mcp.tool
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


@mcp.tool()
async def analyze_repository(
    repo_owner: str,
    repo_name: str,
    analysis_type: str = "overview",
    ctx: Context = None,
) -> str:
    """
    Analyze a GitHub repository using OAuth data + LLM sampling.

    Combines authenticated GitHub API data with AI analysis for insights.

    Args:
        repo_owner: Repository owner/organization
        repo_name: Repository name
        analysis_type: Type of analysis (overview, tech_stack, architecture, security)

    Returns:
        AI-generated analysis based on repository data

    Raises:
        ValueError: If not authenticated, sampling not supported, or API call fails
    """
    token = get_access_token()

    if not token:
        raise ValueError("OAuth authentication required")

    if ctx is None:
        raise ValueError("Context is required for sampling capability")

    try:
        # 1. Fetch repository data via OAuth
        await ctx.info(f"Fetching repository data for {repo_owner}/{repo_name}")

        repo_data = await api_client.get_repository(token, repo_owner, repo_name)
        readme_content = await api_client.get_readme(token, repo_owner, repo_name)
        languages = await api_client.get_repository_languages(token, repo_owner, repo_name)

        # 2. Prepare context for LLM analysis
        context = {
            "repository": {
                "name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "language": repo_data.get("language"),
                "languages": languages,
                "stars": repo_data.get("stargazers_count"),
                "forks": repo_data.get("forks_count"),
                "topics": repo_data.get("topics", []),
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
            },
            "readme_snippet": readme_content[:2000] if readme_content else "No README found"
        }

        # 3. Create analysis prompt based on type
        analysis_prompts = {
            "overview": "Provide a comprehensive analysis of this repository including its purpose, technology stack, and notable features.",
            "tech_stack": "Analyze the technology stack and architecture. Identify frameworks, libraries, and design patterns used.",
            "architecture": "Examine the repository structure and provide insights about the software architecture and organization.",
            "security": "Review for potential security considerations and best practices based on the visible information."
        }

        prompt = f"""
Analyze this GitHub repository data:

{json.dumps(context, indent=2)}

Task: {analysis_prompts.get(analysis_type, analysis_prompts["overview"])}

Provide specific, actionable insights based on the data. Focus on:
- Code quality indicators
- Technology choices and their implications
- Potential improvements or recommendations
- Notable patterns or practices
"""

        # 4. Use sampling to get LLM analysis
        await ctx.info("Requesting AI analysis via sampling...")

        result = await ctx.sample(
            messages=[prompt],
            system_prompt="You are a senior software architect and code reviewer. Provide detailed, technical analysis with specific recommendations.",
            max_tokens=800,
            temperature=0.3  # Lower temperature for more consistent analysis
        )

        # 5. Return structured analysis
        analysis_result = {
            "repository": f"{repo_owner}/{repo_name}",
            "analysis_type": analysis_type,
            "analysis": result.text if hasattr(result, 'text') else str(result),
            "data_sources": ["GitHub API", "Repository metadata", "README content", "Language statistics"]
        }

        logger.info(f"Successfully analyzed repository {repo_owner}/{repo_name}")
        return json.dumps(analysis_result, indent=2)

    except Exception as e:
        error_msg = f"Repository analysis failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise ValueError(error_msg) from e
