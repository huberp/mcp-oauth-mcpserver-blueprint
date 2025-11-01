"""HTTP endpoints for health checks, metrics, and server information."""

import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_server.config import settings

logger = logging.getLogger(__name__)

# Global metrics storage for tool call statistics
_tool_call_counts: dict[str, int] = defaultdict(int)
_server_start_time = datetime.now(UTC)


def increment_tool_call(tool_name: str) -> None:
    """
    Increment the call count for a specific tool.

    Args:
        tool_name: Name of the tool that was called
    """
    _tool_call_counts[tool_name] += 1
    logger.debug(f"Tool call count incremented: {tool_name} = {_tool_call_counts[tool_name]}")


def get_tool_call_counts() -> dict[str, int]:
    """
    Get the current tool call counts.

    Returns:
        Dictionary mapping tool names to call counts
    """
    return dict(_tool_call_counts)


async def health_endpoint(request: Request) -> JSONResponse:
    """
    Health check endpoint.

    Returns server health status and basic diagnostic information.

    Args:
        request: Starlette request object

    Returns:
        JSONResponse with health status
    """
    uptime_seconds = (datetime.now(UTC) - _server_start_time).total_seconds()

    health_data = {
        "status": "healthy",
        "server": settings.server_name,
        "version": settings.server_version,
        "uptime_seconds": round(uptime_seconds, 2),
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }

    logger.debug("Health check requested")
    return JSONResponse(health_data)


async def metrics_endpoint(request: Request) -> JSONResponse:
    """
    Metrics endpoint.

    Returns tool call statistics and other operational metrics.

    Args:
        request: Starlette request object

    Returns:
        JSONResponse with metrics data
    """
    uptime_seconds = (datetime.now(UTC) - _server_start_time).total_seconds()
    tool_counts = get_tool_call_counts()

    metrics_data = {
        "server": settings.server_name,
        "version": settings.server_version,
        "uptime_seconds": round(uptime_seconds, 2),
        "tool_calls": {
            "total": sum(tool_counts.values()),
            "by_tool": tool_counts,
        },
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }

    logger.debug("Metrics requested")
    return JSONResponse(metrics_data)


async def info_endpoint(request: Request) -> JSONResponse:
    """
    Server information endpoint.

    Returns server metadata including version, GitHub info, and configuration.

    Args:
        request: Starlette request object

    Returns:
        JSONResponse with server information
    """
    info_data: dict[str, Any] = {
        "server": {
            "name": settings.server_name,
            "version": settings.server_version,
            "environment": settings.environment,
            "debug": settings.debug,
        },
        "github": {
            "repository": "huberp/mcp-oauth-mcpserver-blueprint",
            "url": "https://github.com/huberp/mcp-oauth-mcpserver-blueprint",
        },
        "oauth": {
            "configured": settings.is_oauth_configured(),
            "provider": "GitHub",
            "scopes": settings.oauth_scopes_list,
        },
        "http": {
            "host": settings.server_host,
            "port": settings.server_port,
            "path": settings.server_path,
        },
        "api": {
            "base_url": settings.api_base_url,
            "timeout": settings.api_timeout,
        },
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }

    logger.debug("Server info requested")
    return JSONResponse(info_data)
