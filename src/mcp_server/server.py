"""MCP Server implementation with OAuth support."""

import logging
from typing import Any

from mcp.server import Server
from mcp.types import Prompt, PromptMessage, TextContent, Tool

from .api_client import APIClient
from .config import settings
from .oauth_handler import OAuthHandler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_mcp_server() -> tuple[Server, OAuthHandler, APIClient]:
    """
    Create and configure the MCP server with OAuth support.

    Returns:
        Tuple of (server, oauth_handler, api_client)
    """
    # Initialize server
    server = Server(settings.server_name)

    # Initialize OAuth and API client
    oauth_handler = OAuthHandler()
    api_client = APIClient(oauth_handler)

    # Register prompt
    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        """List available prompts."""
        return [
            Prompt(
                name="github_user_summary",
                description="Generate a summary of a GitHub user's profile and repositories",
                arguments=[
                    {
                        "name": "username",
                        "description": "GitHub username to summarize",
                        "required": False,
                    }
                ],
            )
        ]

    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> PromptMessage:
        """Get a specific prompt by name."""
        if name != "github_user_summary":
            raise ValueError(f"Unknown prompt: {name}")

        username = arguments.get("username", "authenticated user") if arguments else "authenticated user"

        prompt_text = f"""You are analyzing GitHub data for: {username}

Please use the 'get_github_user_info' tool to fetch user information and repository data.

Based on the retrieved data, provide:
1. A brief summary of the user's profile
2. Top 5 most recently updated repositories
3. Programming languages most commonly used
4. Notable achievements or statistics

Format your response in a clear, readable markdown format."""

        return PromptMessage(
            role="user",
            content=TextContent(type="text", text=prompt_text),
        )

    # Register tool with MCP Spec 2025-06-18 enhancements
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools with structured output schemas."""
        return [
            Tool(
                name="get_github_user_info",
                description="Fetch authenticated GitHub user information and repositories using OAuth. "
                "This tool requires OAuth authentication and retrieves the user's profile and recent repositories. "
                "Returns structured data about the user and their repositories.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "include_repos": {
                            "type": "boolean",
                            "description": "Whether to include repository information",
                            "default": True,
                        },
                        "repo_limit": {
                            "type": "integer",
                            "description": "Maximum number of repositories to fetch",
                            "default": 10,
                            "minimum": 1,
                            "maximum": 100,
                        },
                    },
                },
                # MCP Spec 2025-06-18: Add metadata for better context
                _meta={
                    "version": "1.0.0",
                    "author": "MCP OAuth Server",
                    "requires_auth": True,
                    "api_resource": "https://api.github.com",
                },
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool with given arguments."""
        if name != "get_github_user_info":
            raise ValueError(f"Unknown tool: {name}")

        # Check if OAuth is configured
        if not settings.is_oauth_configured():
            error_msg = (
                "OAuth is not configured. Please set OAUTH_CLIENT_ID and "
                "OAUTH_CLIENT_SECRET environment variables. "
                "See .env.example for details."
            )
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

        # Check if authenticated
        if not oauth_handler.is_authenticated():
            auth_url, state, code_verifier = oauth_handler.get_authorization_url()
            instructions = f"""OAuth authentication required.

Please complete the following steps:
1. Open this URL in your browser: {auth_url}
2. Authorize the application
3. You will be redirected to a callback URL
4. Copy the 'code' parameter from the callback URL
5. Use the code to exchange for an access token

Note: This is a demonstration flow. In production, implement a proper OAuth callback handler.
Code verifier for PKCE (save this): {code_verifier}
State (for verification): {state}"""

            logger.warning("User not authenticated, providing OAuth instructions")
            return [TextContent(type="text", text=instructions)]

        try:
            # Fetch user info
            user_info = await api_client.get_user_info()

            result = {
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
            include_repos = arguments.get("include_repos", True)
            if include_repos:
                repo_limit = arguments.get("repo_limit", 10)
                repos = await api_client.get_user_repos(limit=repo_limit)

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

            import json

            result_text = json.dumps(result, indent=2)
            logger.info("Successfully fetched GitHub user info")
            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            error_msg = f"Error fetching GitHub user info: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    logger.info(f"MCP Server '{settings.server_name}' created successfully")
    return server, oauth_handler, api_client
