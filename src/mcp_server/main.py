"""Main entry point for MCP OAuth Server with HTTP transport."""

import asyncio
import logging
import sys

from .config import settings
from .server import mcp

logger = logging.getLogger(__name__)


async def run_server() -> None:
    """Run the MCP server with HTTP transport."""
    logger.info(f"Starting {settings.server_name} v{settings.server_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"HTTP Server: {settings.server_host}:{settings.server_port}{settings.server_path}")

    # Log OAuth configuration status
    if settings.is_oauth_configured():
        logger.info("OAuth is configured")
        logger.info(f"OAuth scopes: {', '.join(settings.oauth_scopes_list)}")

        # Log authorization metadata for debugging
        auth_metadata = settings.get_authorization_metadata()
        logger.info(f"OAuth Issuer: {auth_metadata['issuer']}")
        logger.info(f"Authorization Endpoint: {auth_metadata['authorization_endpoint']}")
        logger.info(f"Token Endpoint: {auth_metadata['token_endpoint']}")
        logger.info(
            f"Supported Grant Types: {', '.join(auth_metadata['grant_types_supported'])}"
        )
        logger.info(
            f"PKCE Methods: {', '.join(auth_metadata['code_challenge_methods_supported'])}"
        )
        logger.info(f"OAuth Redirect URI: {settings.oauth_redirect_uri}")
    else:
        logger.warning(
            "OAuth is not configured. Please set OAUTH_CLIENT_ID and "
            "OAUTH_CLIENT_SECRET environment variables."
        )

    # Run server with HTTP transport
    logger.info("Starting HTTP server with Streamable HTTP transport")
    logger.info(f"MCP endpoint: http://{settings.server_host}:{settings.server_port}{settings.server_path}")
    logger.info(f"OAuth metadata: http://{settings.server_host}:{settings.server_port}/.well-known/oauth-authorization-server")
    logger.info(f"Health check: http://{settings.server_host}:{settings.server_port}/health")
    
    await mcp.run_async(
        transport="http",
        host=settings.server_host,
        port=settings.server_port,
        path=settings.server_path,
    )


def main() -> None:
    """Main entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
