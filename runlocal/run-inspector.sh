#!/usr/bin/env bash
set -euo pipefail

# Location: runlocal/run-inspector.sh
# Purpose: Load .env.local into environment and start MCP Inspector using runlocal/config.json

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Set the settings file for Pydantic to use .env.local
export SETTINGS_FILE=".env.local"

if [ ! -f ".env.local" ]; then
  echo ".env.local not found. Please create it (copy from .env.example)" >&2
  exit 1
fi

# Export all variables defined in .env.local into the environment for this process (ignores comments and blank lines)
# This avoids embedding secrets in the config.json file.
set -a
. ./.env.local
set +a

echo "Starting MCP Inspector (UI) with config: runlocal/config.json"
mcp-inspector --config runlocal/config.json --server local-server
