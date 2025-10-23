#!/bin/bash
# Run script for MCP OAuth Server

set -e

echo "=== Starting MCP OAuth Server ==="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Using default configuration."
    echo "Copy .env.example to .env and configure OAuth credentials for full functionality."
    echo ""
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Run the server
echo "Starting server..."
python -m mcp_server.main
