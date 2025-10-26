#!/bin/bash
# Stop script for MCP OAuth Server
# This script stops the background server process

set -e

echo "=== Stopping MCP OAuth Server ==="
echo ""

# Define PID file path
PID_FILE=".mcp-server.pid"

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "No PID file found. Server may not be running."
    echo "PID file location: $PID_FILE"
    exit 0
fi

# Read PID from file
PID=$(cat "$PID_FILE")
echo "Found PID: $PID"

# Try to stop the process
if kill -0 "$PID" 2>/dev/null; then
    echo "Stopping process $PID..."
    
    # Try graceful shutdown first (SIGTERM)
    kill "$PID" 2>/dev/null || true
    
    # Wait up to 5 seconds for graceful shutdown
    for i in {1..5}; do
        if ! kill -0 "$PID" 2>/dev/null; then
            break
        fi
        sleep 1
    done
    
    # Force kill if still running
    if kill -0 "$PID" 2>/dev/null; then
        echo "Graceful shutdown failed, forcing termination..."
        kill -9 "$PID" 2>/dev/null || true
        sleep 1
    fi
    
    echo "Server stopped successfully!"
else
    echo "Process $PID is not running (may have already stopped)."
fi

# Remove PID file
rm -f "$PID_FILE"
echo "PID file removed."

echo ""
echo "Server shutdown complete."
