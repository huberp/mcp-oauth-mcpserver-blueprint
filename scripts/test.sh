#!/bin/bash
# Test script for MCP OAuth Server

set -e

echo "=== Running MCP OAuth Server Tests ==="
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    # shellcheck source=/dev/null
    source venv/bin/activate
fi

# Run linting with ruff
echo "Running linting checks..."
ruff check src/ tests/ || true
echo ""

# Run type checking with mypy
echo "Running type checks..."
mypy src/ || true
echo ""

# Run tests with pytest
echo "Running unit tests..."
pytest tests/ -v --cov=src/mcp_server --cov-report=term-missing --cov-report=html

echo ""
echo "=== Tests Complete ==="
echo "Coverage report available in htmlcov/index.html"
echo ""
