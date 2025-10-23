# Test script for MCP OAuth Server (PowerShell)

Write-Host "=== Running MCP OAuth Server Tests ===" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
}

# Run linting with ruff
Write-Host "Running linting checks..." -ForegroundColor Yellow
ruff check src/ tests/
Write-Host ""

# Run type checking with mypy
Write-Host "Running type checks..." -ForegroundColor Yellow
mypy src/
Write-Host ""

# Run tests with pytest
Write-Host "Running unit tests..." -ForegroundColor Yellow
pytest tests/ -v --cov=src/mcp_server --cov-report=term-missing --cov-report=html

Write-Host ""
Write-Host "=== Tests Complete ===" -ForegroundColor Cyan
Write-Host "Coverage report available in htmlcov\index.html"
Write-Host ""
