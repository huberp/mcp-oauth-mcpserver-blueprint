"""MCP Server implementation with OAuth support."""

import json
import logging
from typing import Any

from mcp.server import Server
from mcp.types import (
    ModelHint,
    ModelPreferences,
    Prompt,
    PromptMessage,
    SamplingMessage,
    TextContent,
    Tool,
)

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
            ),
            Tool(
                name="analyze_code_with_llm",
                description="Use LLM sampling to analyze code snippets or GitHub repository data. "
                "This tool demonstrates the MCP sampling capability by requesting the client's "
                "language model to analyze code or provide insights. Requires the client to support "
                "the 'sampling' capability.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Code snippet or data to analyze",
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis to perform",
                            "enum": [
                                "explain",
                                "review",
                                "suggest_improvements",
                                "find_bugs",
                                "security_review",
                            ],
                            "default": "explain",
                        },
                        "max_tokens": {
                            "type": "integer",
                            "description": "Maximum tokens for the LLM response",
                            "default": 500,
                            "minimum": 100,
                            "maximum": 2000,
                        },
                    },
                    "required": ["code"],
                },
                _meta={
                    "version": "1.0.0",
                    "author": "MCP OAuth Server",
                    "requires_sampling": True,
                    "requires_auth": False,
                },
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute a tool with given arguments."""
        if name == "get_github_user_info":
            return await handle_get_github_user_info(arguments)
        elif name == "analyze_code_with_llm":
            return await handle_analyze_code_with_llm(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")

    async def handle_get_github_user_info(arguments: dict[str, Any]) -> list[TextContent]:
        """Handle the get_github_user_info tool."""
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

            result_text = json.dumps(result, indent=2)
            logger.info("Successfully fetched GitHub user info")
            return [TextContent(type="text", text=result_text)]

        except Exception as e:
            error_msg = f"Error fetching GitHub user info: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    async def handle_analyze_code_with_llm(arguments: dict[str, Any]) -> list[TextContent]:
        """Handle the analyze_code_with_llm tool using sampling capability."""
        # Get the request context to access session
        try:
            ctx = server.request_context
            session = ctx.session
        except LookupError:
            error_msg = "Cannot access session context - request context not available"
            logger.error(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

        # Check if client supports sampling capability
        # Access the client's capabilities and check if sampling is present
        try:
            client_capabilities = session.client_params.capabilities if session.client_params else None
            has_sampling = (
                client_capabilities is not None
                and hasattr(client_capabilities, "sampling")
                and client_capabilities.sampling is not None
            )
        except Exception as e:
            logger.warning(f"Error checking client capability: {e}")
            has_sampling = False

        if not has_sampling:
            error_msg = (
                "This tool requires the 'sampling' capability, but your client does not support it. "
                "Please use an MCP client that supports sampling (e.g., Claude Desktop, VSCode with MCP support)."
            )
            logger.warning(error_msg)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

        # Extract arguments
        code = arguments.get("code", "")
        analysis_type = arguments.get("analysis_type", "explain")
        max_tokens = arguments.get("max_tokens", 500)

        if not code:
            return [TextContent(type="text", text="Error: 'code' parameter is required")]

        # Create the analysis prompt based on type
        analysis_prompts = {
            "explain": "Please explain what this code does in clear, simple terms:",
            "review": "Please review this code and provide constructive feedback:",
            "suggest_improvements": "Please suggest improvements for this code:",
            "find_bugs": "Please analyze this code for potential bugs or issues:",
            "security_review": "Please review this code for security vulnerabilities:",
        }

        prompt_prefix = analysis_prompts.get(
            analysis_type, "Please analyze this code:"
        )
        full_prompt = f"{prompt_prefix}\n\n```\n{code}\n```"

        try:
            # Create messages for sampling
            messages = [
                SamplingMessage(
                    role="user",
                    content=TextContent(type="text", text=full_prompt),
                )
            ]

            # Make the sampling request
            logger.info(f"Requesting LLM sampling for code analysis: {analysis_type}")
            result = await session.create_message(
                messages=messages,
                max_tokens=max_tokens,
                system_prompt="You are an expert code analyst. Provide clear, actionable insights.",
                temperature=0.7,
                model_preferences=ModelPreferences(
                    hints=[
                        ModelHint(name="claude-3-5-sonnet"),
                        ModelHint(name="gpt-4"),
                    ],
                    intelligencePriority=0.8,
                    speedPriority=0.5,
                ),
            )

            # Extract the response - handle different content types safely
            response_content = result.content
            if hasattr(response_content, "text"):
                response_text = response_content.text  # type: ignore[attr-defined]
            else:
                response_text = str(response_content)

            model_used = result.model
            stop_reason = result.stopReason

            # Format the response
            formatted_response = f"""# Code Analysis Result

**Analysis Type:** {analysis_type}
**Model Used:** {model_used}
**Stop Reason:** {stop_reason}

## Analysis

{response_text}
"""

            logger.info(f"Successfully completed code analysis using model: {model_used}")
            return [TextContent(type="text", text=formatted_response)]

        except Exception as e:
            error_msg = f"Error during sampling request: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return [TextContent(type="text", text=f"Error: {error_msg}")]

    logger.info(f"MCP Server '{settings.server_name}' created successfully")
    return server, oauth_handler, api_client
