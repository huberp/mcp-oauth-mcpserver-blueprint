#!/bin/bash
# Wrapper script to capture MCP server debug output while preserving stdio for inspector
# Usage: mcp-debug-wrapper.sh <debug_log_file>

DEBUG_LOG_FILE="${1:-/tmp/mcp-debug.log}"

# Save original stdout to fd 3 and stderr to fd 4
exec 3>&1 4>&2

# Run MCP server with DEBUG logging
# Redirect stderr to log file, stdout to saved fd 3
LOG_LEVEL=DEBUG python3 -m mcp_server.main 2>"$DEBUG_LOG_FILE" 1>&3
