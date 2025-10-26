#!/usr/bin/env bash
set -euo pipefail

# Location: runlocal/run-inspector.sh
# Purpose: Start MCP Inspector using HTTP transport with runlocal/config.json
# Note: With HTTP transport, the server must be started separately before running the inspector

START_SERVER=false
CLI_MODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --start-server)
            START_SERVER=true
            shift
            ;;
        --cli)
            CLI_MODE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--start-server] [--cli]"
            exit 1
            ;;
    esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Function to check if server is running
check_server_running() {
    if curl -s -f -o /dev/null "http://localhost:8000/health" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Start server if requested
if [ "$START_SERVER" = true ]; then
    echo "Starting MCP server..."
    
    # Check if already running
    if check_server_running; then
        echo "Server is already running at http://localhost:8000"
    else
        # Set the settings file for Pydantic to use .env.local
        export SETTINGS_FILE=".env.local"
        
        if [ ! -f ".env.local" ]; then
            echo ".env.local not found. Please create it (copy from .env.example)" >&2
            exit 1
        fi
        
        # Start the server in background
        ./scripts/run.sh
        
        # Wait for server to be ready
        echo "Waiting for server to start..."
        MAX_ATTEMPTS=30
        ATTEMPT=0
        while ! check_server_running && [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
            sleep 1
            ATTEMPT=$((ATTEMPT + 1))
            echo -n "."
        done
        echo ""
        
        if ! check_server_running; then
            echo "Server failed to start after $MAX_ATTEMPTS seconds" >&2
            exit 1
        fi
        
        echo "Server is ready!"
        echo ""
    fi
fi

# Check if server is running
if ! check_server_running; then
    echo "Error: MCP server is not running!" >&2
    echo "" >&2
    echo "The HTTP transport requires the server to be running before starting the inspector." >&2
    echo "" >&2
    echo "To start the server:" >&2
    echo "  1. Run: ./scripts/run.sh" >&2
    echo "     (or use --start-server flag to auto-start)" >&2
    echo "  2. Wait for server to be ready at http://localhost:8000" >&2
    echo "  3. Then run this script again" >&2
    echo "" >&2
    echo "Quick start: ./runlocal/run-inspector.sh --start-server" >&2
    exit 1
fi

echo "MCP server is running at http://localhost:8000"
echo ""

# Build inspector command
CMD="npx @modelcontextprotocol/inspector --config runlocal/config.json --server local-server"
if [ "$CLI_MODE" = true ]; then
    # CLI mode for automated testing
    CMD="$CMD --cli --method tools/call --tool-name get_github_user_info"
fi

echo "Starting MCP Inspector with config: runlocal/config.json"
echo "Transport: HTTP (http://localhost:8000/mcp)"
echo ""

eval "$CMD"

