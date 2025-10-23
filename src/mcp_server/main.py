"""Main entry point for MCP OAuth Server."""

import asyncio
import logging
import sys

from mcp.server.stdio import stdio_server

from .config import settings
from .server import create_mcp_server

logger = logging.getLogger(__name__)


async def run_server() -> None:
    """Run the MCP server with stdio transport."""
    logger.info(f"Starting {settings.server_name} v{settings.server_version}")
    logger.info(f"Environment: {settings.environment}")

    # Create server
    server, oauth_handler, api_client = create_mcp_server()

    # Log OAuth configuration status
    if settings.is_oauth_configured():
        logger.info("OAuth is configured")
        logger.info(f"OAuth scopes: {', '.join(settings.oauth_scopes_list)}")
    else:
        logger.warning(
            "OAuth is not configured. Please set OAUTH_CLIENT_ID and "
            "OAUTH_CLIENT_SECRET environment variables."
        )

    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server running on stdio transport")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
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
