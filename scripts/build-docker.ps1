# Docker build script for MCP OAuth Server (PowerShell)

Write-Host "=== Building MCP OAuth Server Docker Image ===" -ForegroundColor Cyan
Write-Host ""

# Build the Docker image
docker build -t mcp-oauth-server:latest .

Write-Host ""
Write-Host "=== Build Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Image: mcp-oauth-server:latest"
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Configure .env file with OAuth credentials"
Write-Host "2. Run with docker-compose: docker-compose up"
Write-Host "   OR"
Write-Host "   Run directly: docker run --env-file .env -i mcp-oauth-server:latest"
Write-Host ""
