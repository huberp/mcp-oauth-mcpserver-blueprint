"""MCP Server implementation with OAuth support using FastMCP and HTTP transport."""

import json
import logging
from datetime import datetime, timedelta
from typing import Any

from fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse

from .api_client import APIClient
from .config import settings
from .oauth_handler import OAuthHandler

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(settings.server_name)

# Initialize OAuth and API client (shared across requests)
oauth_handler = OAuthHandler()
api_client = APIClient(oauth_handler)

# Simple in-memory session storage for OAuth state
# In production, use Redis, database, or encrypted cookies
oauth_sessions: dict[str, dict[str, Any]] = {}

def cleanup_expired_sessions() -> None:
    """Remove expired OAuth sessions."""
    now = datetime.now()
    expired = [
        state for state, data in oauth_sessions.items()
        if data.get("expires_at", now) < now
    ]
    for state in expired:
        oauth_sessions.pop(state, None)
    if expired:
        logger.info(f"Cleaned up {len(expired)} expired OAuth sessions")


@mcp.prompt()
async def github_user_summary(username: str = "authenticated user") -> str:
    """
    Generate a summary of a GitHub user's profile and repositories.

    Args:
        username: GitHub username to summarize (defaults to authenticated user)

    Returns:
        A prompt template for analyzing GitHub user data
    """
    prompt_text = f"""You are analyzing GitHub data for: {username}

Please use the 'get_github_user_info' tool to fetch user information and repository data.

Based on the retrieved data, provide:
1. A brief summary of the user's profile
2. Top 5 most recently updated repositories
3. Programming languages most commonly used
4. Notable achievements or statistics

Format your response in a clear, readable markdown format."""

    return prompt_text


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
    # Check if OAuth is configured
    if not settings.is_oauth_configured():
        error_msg = (
            "OAuth is not configured. Please set OAUTH_CLIENT_ID and "
            "OAUTH_CLIENT_SECRET environment variables. "
            "See .env.example for details."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    # Check if authenticated
    if not oauth_handler.is_authenticated():
        # Get structured authorization error response
        auth_error = oauth_handler.get_authorization_error_response()

        # Format as JSON for client consumption
        error_message = json.dumps(auth_error, indent=2)

        # Add user-friendly instructions
        instructions = f"""OAuth authentication required.

Authorization Error Details:
{error_message}

To authenticate:
1. Use the authorization_url from the error data above
2. Complete the OAuth flow with PKCE (code_challenge_method: S256)
3. Exchange the authorization code for an access token at token_url
4. Include the resource parameter: {oauth_handler.get_resource_uri()}

Note: This structured error response enables MCP clients to automate the OAuth flow.
For manual testing, you can use the authorization_url directly or visit /oauth/authorize."""

        logger.warning("User not authenticated, providing structured OAuth error response")
        raise ValueError(instructions)

    try:
        # Fetch user info
        user_info = await api_client.get_user_info()

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
        return result_text

    except Exception as e:
        error_msg = f"Error fetching GitHub user info: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise ValueError(error_msg) from e


@mcp.tool()
async def analyze_code_with_llm(
    code: str,
    analysis_type: str = "explain",
    max_tokens: int = 500
) -> str:
    """
    Use LLM sampling to analyze code snippets or GitHub repository data.

    This tool demonstrates the MCP sampling capability by requesting the client's
    language model to analyze code or provide insights. Requires the client to support
    the 'sampling' capability.

    Args:
        code: Code snippet or data to analyze
        analysis_type: Type of analysis to perform (explain, review, suggest_improvements,
                      find_bugs, security_review)
        max_tokens: Maximum tokens for the LLM response (100-2000, default: 500)

    Returns:
        Analysis result with model information

    Raises:
        ValueError: If code is empty or client doesn't support sampling
    """
    if not code:
        raise ValueError("'code' parameter is required")

    # Validate analysis type
    valid_types = ["explain", "review", "suggest_improvements", "find_bugs", "security_review"]
    if analysis_type not in valid_types:
        raise ValueError(f"Invalid analysis_type. Must be one of: {', '.join(valid_types)}")

    # Validate max_tokens
    if max_tokens < 100 or max_tokens > 2000:
        raise ValueError("max_tokens must be between 100 and 2000")

    # Create the analysis prompt based on type
    analysis_prompts = {
        "explain": "Please explain what this code does in clear, simple terms:",
        "review": "Please review this code and provide constructive feedback:",
        "suggest_improvements": "Please suggest improvements for this code:",
        "find_bugs": "Please analyze this code for potential bugs or issues:",
        "security_review": "Please review this code for security vulnerabilities:",
    }

    prompt_prefix = analysis_prompts[analysis_type]
    full_prompt = f"{prompt_prefix}\n\n```\n{code}\n```"

    # Note: FastMCP doesn't expose sampling API directly yet
    # For now, we return a placeholder that explains the limitation
    result = f"""# Code Analysis Request

**Analysis Type:** {analysis_type}
**Code Length:** {len(code)} characters

## Requested Analysis

{full_prompt}

**Note:** This tool requires MCP sampling capability support. The server is configured
to request analysis from the client's LLM, but the current FastMCP implementation
does not yet expose the sampling API in the same way as the old MCP SDK.

For now, you can:
1. Use the prompt above to manually analyze the code
2. Wait for FastMCP to add sampling support
3. Use the old MCP SDK with stdio transport for sampling

**Maximum Tokens:** {max_tokens}
"""

    return result


# Custom HTTP routes for OAuth flow
@mcp.custom_route("/.well-known/oauth-authorization-server", methods=["GET"])
async def oauth_metadata(request: Request) -> JSONResponse:
    """
    RFC 8414 Authorization Server Metadata endpoint.

    Provides machine-readable OAuth server metadata for client autodiscovery.
    """
    logger.info("Serving OAuth authorization server metadata")
    metadata = settings.get_authorization_metadata()
    return JSONResponse(metadata)


@mcp.custom_route("/oauth/authorize", methods=["GET"])
async def oauth_authorize(request: Request) -> RedirectResponse:
    """
    OAuth authorization endpoint.

    Initiates the OAuth authorization flow by redirecting to the GitHub OAuth page.
    """
    logger.info("Initiating OAuth authorization flow")
    cleanup_expired_sessions()

    # Generate authorization URL with PKCE
    auth_url, state, code_verifier = oauth_handler.get_authorization_url()

    # Store session data for callback
    oauth_sessions[state] = {
        "code_verifier": code_verifier,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=10),  # 10 minute expiry
    }

    logger.info(f"OAuth session created. State: {state}")
    logger.info(f"Active OAuth sessions: {len(oauth_sessions)}")

    # Redirect to GitHub OAuth page
    return RedirectResponse(url=auth_url)


@mcp.custom_route("/oauth/callback", methods=["GET"])
async def oauth_callback(request: Request) -> HTMLResponse:
    """
    OAuth callback endpoint.

    Handles the OAuth callback from GitHub and exchanges the authorization code for tokens.
    """
    logger.info("Received OAuth callback")
    cleanup_expired_sessions()

    # Get authorization code and state from query parameters
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")

    if error:
        logger.error(f"OAuth error: {error}")
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .error {{ color: #d32f2f; background: #ffebee; padding: 20px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>OAuth Authorization Failed</h1>
            <div class="error">
                <strong>Error:</strong> {error}
            </div>
            <p>Please try again or contact support if the problem persists.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)

    if not code or not state:
        logger.error("Missing authorization code or state")
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Error</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .error { color: #d32f2f; background: #ffebee; padding: 20px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <h1>OAuth Authorization Failed</h1>
            <div class="error">
                <strong>Error:</strong> Missing authorization code or state parameter
            </div>
            <p>The OAuth callback was incomplete. Please try again.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)

    # Retrieve session data
    session_data = oauth_sessions.pop(state, None)

    if not session_data:
        logger.error(f"Invalid or expired state: {state}")
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Error</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .error { color: #d32f2f; background: #ffebee; padding: 20px; border-radius: 4px; }
            </style>
        </head>
        <body>
            <h1>OAuth Authorization Failed</h1>
            <div class="error">
                <strong>Error:</strong> Invalid or expired session
            </div>
            <p>Your OAuth session has expired or is invalid. Please start the authorization flow again.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)

    code_verifier = session_data["code_verifier"]

    try:
        # Exchange code for token
        token = await oauth_handler.exchange_code_for_token(
            code=code,
            code_verifier=code_verifier,
            redirect_uri=settings.oauth_redirect_uri
        )

        logger.info("Successfully exchanged authorization code for access token")

        # Success page
        success_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Success</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .success {{ color: #2e7d32; background: #e8f5e9; padding: 20px; border-radius: 4px; }}
                .info {{ background: #f5f5f5; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                code {{ background: #263238; color: #aed581; padding: 2px 6px; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h1>✓ OAuth Authorization Successful</h1>
            <div class="success">
                <strong>Success!</strong> You have been authenticated with GitHub.
            </div>
            <div class="info">
                <p><strong>Token Information:</strong></p>
                <ul>
                    <li>Access Token: <code>***{oauth_handler.access_token[-8:] if oauth_handler.access_token else "N/A"}</code></li>
                    <li>Token Type: <code>{token.get("token_type", "bearer")}</code></li>
                    <li>Scopes: <code>{token.get("scope", "N/A")}</code></li>
                </ul>
            </div>
            <p>You can now close this window and use the MCP server with authentication.</p>
            <p>The server has stored your access token and will use it for GitHub API requests.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=success_html, status_code=200)

    except Exception as e:
        logger.error(f"Token exchange failed: {e}", exc_info=True)
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OAuth Error</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                .error {{ color: #d32f2f; background: #ffebee; padding: 20px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>OAuth Token Exchange Failed</h1>
            <div class="error">
                <strong>Error:</strong> {str(e)}
            </div>
            <p>Failed to exchange authorization code for access token.</p>
            <p>Please try again or check your OAuth configuration.</p>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> PlainTextResponse:
    """Health check endpoint."""
    return PlainTextResponse("OK")


# Export the FastMCP app for other modules to use
def get_app() -> FastMCP:
    """Get the FastMCP application instance."""
    return mcp


def create_mcp_server() -> tuple[FastMCP, OAuthHandler, APIClient]:
    """
    Create and configure the MCP server with OAuth support.

    This function maintains compatibility with the old API while using FastMCP.

    Returns:
        Tuple of (mcp_server, oauth_handler, api_client)
    """
    logger.info(f"MCP Server '{settings.server_name}' created successfully")
    return mcp, oauth_handler, api_client
