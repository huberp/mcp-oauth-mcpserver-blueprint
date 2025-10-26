#!/bin/bash
# Run script for MCP OAuth Server
# This script starts the server in the background and writes a PID file

set -e

FOREGROUND=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --foreground|-f)
            FOREGROUND=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--foreground|-f]"
            exit 1
            ;;
    esac
done

echo "=== Starting MCP OAuth Server ==="
echo ""

# Define PID file path
PID_FILE=".mcp-server.pid"

# Check if server is already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Server is already running with PID $OLD_PID"
        echo "Use scripts/stop.sh to stop it first."
        exit 1
    else
        # Process no longer exists, remove stale PID file
        rm -f "$PID_FILE"
    fi
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Using default configuration."
    echo "Copy .env.example to .env and configure OAuth credentials for full functionality."
    echo ""
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    set -a
    # shellcheck source=/dev/null
    . .env
    set +a
fi

# Build python command
PYTHON_CMD="python"
if [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
fi

if [ "$FOREGROUND" = true ]; then
    # Run in foreground (interactive mode)
    echo "Starting server in foreground mode..."
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    "$PYTHON_CMD" -m mcp_server.main
else
    # Run in background mode
    echo "Starting server in background mode..."
    
    # Start process in background
    nohup "$PYTHON_CMD" -m mcp_server.main > /dev/null 2>&1 &
    SERVER_PID=$!
    
    # Wait a moment to ensure process started
    sleep 2
    
    # Check if process is still running
    if ! kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "Error: Server failed to start"
        exit 1
    fi
    
    # Save PID to file
    echo "$SERVER_PID" > "$PID_FILE"
    
    echo "Server started successfully!"
    echo "PID: $SERVER_PID"
    echo "PID file: $PID_FILE"
    echo ""
    echo "Server endpoints:"
    echo "  MCP:    http://localhost:8000/mcp"
    echo "  OAuth:  http://localhost:8000/oauth/authorize"
    echo "  Health: http://localhost:8000/health"
    echo ""
    echo "To stop the server, run: ./scripts/stop.sh"
fi

