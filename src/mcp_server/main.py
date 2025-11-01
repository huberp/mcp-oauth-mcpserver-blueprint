"""MCP OAuth Server entry point with HTTP transport."""

import asyncio
import logging
import sys

from mcp_server.config import settings
from mcp_server.server import mcp

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run_server() -> None:
    """Start MCP server with HTTP transport."""
    logger.info(f"Starting {settings.server_name} v{settings.server_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"HTTP Server: {settings.server_host}:{settings.server_port}{settings.server_path}")

    # Start HTTP server with Streamable HTTP transport
    await mcp.run_async(
        transport="http",
        host=settings.server_host,
        port=settings.server_port,
        path=settings.server_path,
    )


def main() -> None:
    """Entry point - starts the server."""
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
