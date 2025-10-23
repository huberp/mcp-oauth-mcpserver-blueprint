#!/bin/bash
# Docker build script for MCP OAuth Server

set -e

echo "=== Building MCP OAuth Server Docker Image ==="
echo ""

# Build the Docker image
docker build -t mcp-oauth-server:latest .

echo ""
echo "=== Build Complete ==="
echo ""
echo "Image: mcp-oauth-server:latest"
echo ""
echo "Next steps:"
echo "1. Configure .env file with OAuth credentials"
echo "2. Run with docker-compose: docker-compose up"
echo "   OR"
echo "   Run directly: docker run --env-file .env -i mcp-oauth-server:latest"
echo ""
